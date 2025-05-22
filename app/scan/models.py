from django.db import models
from django.contrib.auth.models import User

def model_result_default():
    return {"class": "prediction"}

class AnalysisResult(models.Model):
    # store the user it belongs to
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analysis_results')
    # store the date it was created
    created_at = models.DateTimeField(auto_now_add=True)
    # store the file statistics
    filename = models.CharField(max_length=255)
    filesize = models.BigIntegerField()
    file_hash = models.CharField(max_length=64)
    # store the image representation
    img_base64 = models.TextField()
    # store the model results
    model_result = models.JSONField(default=model_result_default)
    # string representation
    def __str__(self):
        return f"Scan by {self.user.username}: {self.filename}"