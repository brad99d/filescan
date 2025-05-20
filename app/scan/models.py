from django.db import models
from django.contrib.auth.models import User

# Create your models here.
def model_result_default():
    return {"class": "prediction"}

class AnalysisResult(models.Model):
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analysis_results')
    created_at = models.DateTimeField(auto_now_add=True)
    # uploaded file
    filename = models.CharField(max_length=255)
    filesize = models.BigIntegerField()
    file_hash = models.CharField(max_length=64)
    img_base64 = models.TextField() # bin_image = models.FileField(upload_to='images/')
    # model results
    model_result = models.JSONField(default=model_result_default)
    # string representation
    def __str__(self):
        return f"Scan by {self.user.username}: {self.filename}"