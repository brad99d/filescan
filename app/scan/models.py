from django.db import models
from django.contrib.auth.models import User

# Create your models here.
def classification_result_default():
    return {"family": "prediction"}

class Result(models.Model):
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='results')
    created_at = models.DateTimeField(auto_now_add=True)
    # uploaded file
    filename = models.CharField(max_length=255)
    filesize = models.BigIntegerField()
    file_hash = models.CharField(max_length=255)
    bin_image = models.FileField(upload_to='images/')
    # classification results
    classification_results = models.JSONField(default=classification_result_default)
    # string representation
    def __str__(self):
        return self.filename