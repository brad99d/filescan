from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# imports for model
import base64
import hashlib
from django.contrib.auth.decorators import login_required
from . import scanner
from . import malware_dictionary

# Create your views here.
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

@login_required()
def dashboard(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        img_bytes = file.read()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        img_data_url = f"data:image/png;base64,{img_base64}"

        filename = shorten_filename(file.name)
        file_hash = hashlib.md5(img_bytes).hexdigest()
        filesize = format_file_size(file.size)

        model_result = scanner.run_model(img_bytes)
        category_result = scanner.get_category_results(model_result)

        print("( NEW ANALYSIS )")
        print(model_result)

        family_summary = scanner.summarise_results(model_result)
        category_summary = scanner.summarise_results(category_result)

        print(family_summary)
        print(category_summary)

        family_results = [(name, round(float(prob) * 100, 2)) for name, prob in family_summary]
        category_results = [(name, round(float(prob) * 100, 2)) for name, prob in category_summary]

        return render(request, 'scan/dashboard.html', {
            'filename': filename,
            'hash': file_hash,
            'filesize': filesize,
            'prediction': model_result,
            'img_url': img_data_url,
            'category_results': category_results,
            'family_results': family_results,
        })
    return render(request, 'scan/dashboard.html')