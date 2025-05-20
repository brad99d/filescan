from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import AnalysisResult
# imports for model
import base64
import hashlib
from django.contrib.auth.decorators import login_required
from . import scanner
from . import malware_dictionary
import numpy as np

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

# convert to native python types
def to_python(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, dict):
        return {k: to_python(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_python(v) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(to_python(v) for v in obj)
    elif isinstance(obj, set):
        return [to_python(v) for v in obj]
    return obj

@login_required()
def dashboard(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        img_bytes = file.read()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        file_hash = hashlib.md5(img_bytes).hexdigest()

        model_result = scanner.run_model(img_bytes)
        model_result_py = to_python(model_result)

        AnalysisResult.objects.create(
            user=request.user,
            filename=file.name,
            filesize=file.size,
            file_hash=file_hash,
            img_base64=img_base64,
            model_result=model_result_py,
        )

    # get all results for the user
    user_results = request.user.analysis_results.all().order_by('-created_at')
    # process the results before passing to the template
    processed_results = []
    for result in user_results:
        # summarise family results
        family_summary = scanner.summarise_results(result.model_result)
        family_summary_formatted = [(name, round(float(prob) * 100, 2)) for name, prob in family_summary]
        # get and summarise category results
        category_results = scanner.get_category_results(result.model_result)
        category_summary = scanner.summarise_results(category_results)
        category_summary_formatted = [(name, round(float(prob) * 100, 2)) for name, prob in category_summary]
        # get behaviour details
        behaviour_summary = scanner.get_behaviour_summary(family_summary[0][0])
        # format the results for the template
        processed_results.append({
            'id': result.id,
            'filename': shorten_filename(result.filename),
            'filesize': format_file_size(result.filesize),
            'file_hash': result.file_hash,
            'img_base64': f"data:image/png;base64,{result.img_base64}",
            'created_at': result.created_at,
            # results
            'top_family': family_summary[0][0],
            'family_results': family_summary_formatted,
            'top_category': category_summary[0][0],
            'category_results': category_summary_formatted,
            'behaviour_summary': behaviour_summary,
        })
    return render(request, 'scan/dashboard.html', {
        'user_results': processed_results,
    })