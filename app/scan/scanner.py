import io
from PIL import Image
import keras
from collections import defaultdict
import numpy as np
from . import malware_dictionary
from bin2png import file_to_png
import tempfile
import base64

# malware family names
category_names = ['Adposhel', 'Agent', 'Allaple', 'Amonetize', 'Androm',
                  'Autorun', 'BrowseFox', 'Dinwod', 'Elex', 'Expiro',
                  'Fasong', 'HackKMS', 'Hlux', 'Injector', 'InstallCore',
                  'MultiPlug', 'Neoreklami', 'Neshta', 'Other', 'Regrun',
                  'Sality', 'Snarasite', 'Stantinko', 'VBA', 'VBKrypt',
                  'Vilsel']

# pretend BytesIO has a name attribute as that is what bin2png expects
class NamedBytesIO(io.BytesIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'not_stdout'

# convert binary file into an image representation
def bin_to_png(file_bytes, size=(300, 300)):
    # store the file temporarily for conversion
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        tmp.seek(0)
        # convert the binary file to PNG, store it in memory
        output_buffer = NamedBytesIO()
        file_to_png(tmp, output_buffer, verbose=False, no_progress=True, dimensions=(size[0], None))
        png_bytes = output_buffer.getvalue()
        # load the image from bytes
        image = Image.open(io.BytesIO(png_bytes))
        # resize the image
        resized_image = image.resize(size, Image.BILINEAR)
        # save the resized image to bytes
        resized_buffer = io.BytesIO()
        resized_image.save(resized_buffer, format='PNG')
        resized_buffer.write(b'X')
        return resized_buffer.getvalue()

def run_model(image_bytes):
    identity_model_result = identity_model(image_bytes)
    category_model_result = category_model(image_bytes)
    return {
        "identity" : identity_model_result,
        "category" : list(zip(category_names, category_model_result))
    }

def identity_model(image_bytes):
    # set the image size as expected by the model
    image_size = (32, 32)
    # load the model
    model = keras.saving.load_model('scan/models/mnist_model_1.keras')
    # read the image
    image_io = io.BytesIO(image_bytes)
    # convert the image to grayscale as expected by the model
    image_conv = Image.open(image_io).convert('L')
    image_conv_io = io.BytesIO()
    image_conv.save(image_conv_io, format='PNG')
    image_conv_io.seek(0)
    # run the model using the image
    img = keras.utils.load_img(image_conv_io, target_size=image_size)
    img_array = keras.utils.img_to_array(img)
    img_array = keras.ops.expand_dims(img_array, 0)
    # store the probabilities
    predictions = model.predict(img_array)
    probabilities = keras.ops.softmax(predictions[0]).numpy()
    # return the probabilities
    return [float(probabilities[0]), float(sum(probabilities[1:]))]

def category_model(image_bytes):
    # set the image size as expected by the model
    image_size = (128, 8)
    # load the model
    model = keras.saving.load_model('scan/models/malevis_model_5.keras')
    # read the image
    image_io = io.BytesIO(image_bytes)
    img = keras.utils.load_img(image_io, target_size=image_size)
    img_array = keras.utils.img_to_array(img)
    img_array = keras.ops.expand_dims(img_array, 0)
    # run the model and store the probabilities
    predictions = model.predict(img_array)
    probabilities = keras.ops.softmax(predictions[0]).numpy()
    # return the probabilities
    return probabilities

# create a list of probabilities based on categories
def get_category_results(family_results):
    category_results = defaultdict(float)
    for family, score in family_results:
        category = malware_dictionary.reference.get(family, {}).get('category', 'Unknown')
        category_results[category] += score
    return list(category_results.items())

# cull results based on a probability threshold and maximum number of results
def summarise_results(results, threshold=0.0001, max_results=4):
    summarised_results = defaultdict(float)
    # collect culled results into an "other" category
    other_score = 0.0
    # cull by threshold
    for family, score in results:
        if family == 'Other':
            other_score += score
        elif score < threshold:
            other_score += score
        else:
            summarised_results[family] = score
    # sort all by score
    sorted_items = sort_results(summarised_results)
    # return only the top results
    top_items = sorted_items[:max_results]
    overflow_items = sorted_items[max_results:]
    # place all culled results into the "other" category
    for _, score in overflow_items:
        other_score += score
    if other_score > 0:
        top_items.append(('Other', other_score))
    # return the summarised results, sorted
    return sort_results(dict(top_items))

# summarise the identity results
def summarise_identity_results(identity_results, results):
    summary = [None, None]
    summary[0] = identity_results[0] if identity_results[0] > identity_results[1] else identity_results[1]
    summary[1] = True if base64.b64decode(results.img_base64)[-1:] == b"X" else False
    return summary

# sort the results based on probability
def sort_results(results):
    return sorted(results.items(), key=lambda x: x[1], reverse=True)

# get the summary stored in the malware dictionary
def get_summary(family):
    return malware_dictionary.reference.get(family, {}).get('summary', 'Malicious code was detected, proceed with caution.')

# get the behaviour stored in the malware dictionary
def get_behaviour(family):
    return malware_dictionary.reference.get(family, {}).get('behaviour', 'Malicious code was detected, proceed with caution.')