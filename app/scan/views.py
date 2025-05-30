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
from django.shortcuts import get_object_or_404, redirect

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'

# converts the filesize into a readable format
def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 ** 2:
        return f'{size_bytes / 1024:.2f} KB'
    elif size_bytes < 1024 ** 3:
        return f'{size_bytes / (1024 ** 2):.2f} MB'
    else:
        return f'{size_bytes / (1024 ** 3):.2f} GB'

# shortens the filename for the user interface
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

def process_results(results):
    # process the results before passing to the template
    processed_results = []
    for result in results:
        raw_identity_results = result.model_result.get("identity")
        raw_category_results = result.model_result.get("category")
        # get identity results
        identity_results_formatted = [round(float(prob) * 100, 2) for prob in raw_identity_results]
        identity_results = scanner.summarise_identity_results(identity_results_formatted, result)
        # summarise family results
        family_summary = scanner.summarise_results(raw_category_results)
        family_summary_formatted = [(name, round(float(prob) * 100, 2)) for name, prob in family_summary]
        # get and summarise category results
        category_results = scanner.get_category_results(raw_category_results)
        category_summary = scanner.summarise_results(category_results)
        category_summary_formatted = [(name, round(float(prob) * 100, 2)) for name, prob in category_summary]
        # get behaviour details
        summary = scanner.get_summary(family_summary[0][0])
        behaviour = scanner.get_behaviour(family_summary[0][0])
        # get identity details
        identity_result = identity_results[0]
        is_benign = identity_results[1]
        # format the results for the template
        processed_results.append({
            'id': result.id,
            'filename': shorten_filename(result.filename),
            'filesize': format_file_size(result.filesize),
            'file_hash': result.file_hash,
            'img_base64': f"data:image/png;base64,{result.img_base64}",
            'created_at': result.created_at,
            # results
            'is_benign': is_benign,
            'identity_result': identity_result,
            'top_family': family_summary[0][0],
            'family_results': family_summary_formatted,
            'top_category': category_summary[0][0],
            'category_results': category_summary_formatted,
            'summary': summary,
            'behaviour': behaviour,
        })
    return processed_results

# dashboard view
@login_required()
def dashboard(request):
    # if a file has been sent to the server for analysis
    if request.method == 'POST' and request.FILES.get('file'):
        # read the file
        file = request.FILES['file']
        file_bytes = file.read()
        # get file statistics
        file_hash = hashlib.md5(file_bytes).hexdigest()
        file_name = file.name
        filesize = file.size
        # if the file is a png, skip binary to image conversion
        if file_bytes[:8] == PNG_SIGNATURE:
            img_bytes = file_bytes
        else:
            # convert the binary to an image
            img_bytes = scanner.bin_to_png(file_bytes)
        # create a base64 representation, to avoid storing actual image files
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        # run the model on the image
        model_result = scanner.run_model(img_bytes)
        # convert the values to native python values
        model_result_py = to_python(model_result)
        # store the result in the database
        AnalysisResult.objects.create(
            user=request.user,
            filename=file_name,
            filesize=filesize,
            file_hash=file_hash,
            img_base64=img_base64,
            model_result=model_result_py,
        )
    # get all results for the user
    user_results = request.user.analysis_results.all().order_by('-created_at')
    processed_results = process_results(user_results)
    return render(request, 'scan/dashboard.html', {
        'user_results': processed_results,
    })

# allows users to delete a result
@login_required()
def delete_result(request, result_id):
    # get the result object based on the id
    result = get_object_or_404(AnalysisResult, id=result_id)
    # make sure the user owns the result
    if request.user != result.user:
        # if the user does not own the result, redirect to the dashboard
        return redirect('dashboard')
    # if the user owns the result, delete it
    result.delete()
    return redirect('dashboard')
