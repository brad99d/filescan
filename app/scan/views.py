from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# imports for model
import base64
import io
from PIL import Image
import keras
import hashlib

# Create your views here.

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

    class_names = ['Adposhel', 'Agent', 'Allaple', 'Amonetize', 'Androm', 'Autorun', 'BrowseFox', 'Dinwod', 'Elex', 'Expiro', 'Fasong', 'HackKMS', 'Hlux', 'Injector', 'InstallCore', 'MultiPlug', 'Neoreklami', 'Neshta', 'Other', 'Regrun', 'Sality', 'Snarasite', 'Stantinko', 'VBA', 'VBKrypt', 'Vilsel']

    results = sorted(zip(class_names, probabilities), key=lambda x: x[1], reverse=True)

    top_prediction = results[0][0]
    top_confidence = results[0][1]

    return {
        'summary': top_prediction,
        'results': results[:5]
    }

def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 ** 2:
        return f'{size_bytes / 1024:.2f} KB'
    elif size_bytes < 1024 ** 3:
        return f'{size_bytes / (1024 ** 2):.2f} MB'
    else:
        return f'{size_bytes / (1024 ** 3):.2f} GB'

def shorten_filename(filename, max_length=30):
    if len(filename) <= max_length:
        return filename
    name, dot, ext = filename.rpartition('.')
    short_name = f"{name[:15]}...{name[-10:]}.{ext}" if ext else f"{filename[:max_length-3]}..."
    return short_name

def dashboard(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        img_bytes = file.read()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        img_data_url = f"data:image/png;base64,{img_base64}"

        filename = shorten_filename(file.name)
        file_hash = hashlib.md5(img_bytes).hexdigest()
        filesize = format_file_size(file.size)

        model_result = run_model(img_bytes)

        return render(request, 'scan/dashboard.html', {
            'filename': filename,
            'hash': file_hash,
            'filesize': filesize,
            'prediction': model_result['summary'],
            'img_url': img_data_url,
            'results': model_result['results']
        })
    return render(request, 'scan/dashboard.html')