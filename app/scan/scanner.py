import io
from PIL import Image
import keras
from collections import defaultdict
import numpy as np
from . import malware_dictionary

# Model Logic
def run_model(image_bytes):
    image_size = (128, 8)
    model = keras.saving.load_model('scan/models/classification_model_5.keras')

    image_io = io.BytesIO(image_bytes)
    img = keras.utils.load_img(image_io, target_size=image_size)
    img_array = keras.utils.img_to_array(img)
    img_array = keras.ops.expand_dims(img_array, 0)

    predictions = model.predict(img_array)
    probabilities = keras.ops.softmax(predictions[0]).numpy()

    # family names
    class_names = ['Adposhel', 'Agent', 'Allaple', 'Amonetize', 'Androm', 'Autorun', 'BrowseFox', 'Dinwod', 'Elex', 'Expiro', 'Fasong', 'HackKMS', 'Hlux', 'Injector', 'InstallCore', 'MultiPlug', 'Neoreklami', 'Neshta', 'Other', 'Regrun', 'Sality', 'Snarasite', 'Stantinko', 'VBA', 'VBKrypt', 'Vilsel']

    return list(zip(class_names, probabilities))

def get_category_results(family_results):
    category_results = defaultdict(float)
    for family, score in family_results:
        category = malware_dictionary.reference.get(family, {}).get('category', 'Unknown')
        category_results[category] += score
    return list(category_results.items())

def summarise_results(results, threshold=0.0001, max_results=4):
    summarised_results = defaultdict(float)
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
    sorted_items = sorted(summarised_results.items(), key=lambda x: x[1], reverse=True)
    top_items = sorted_items[:max_results]
    overflow_items = sorted_items[max_results:]
    for _, score in overflow_items:
        other_score += score
    if other_score > 0:
        top_items.append(('Other', other_score))
    return sort_results(dict(top_items))

def sort_results(results):
    return sorted(results.items(), key=lambda x: x[1], reverse=True)