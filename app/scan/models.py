from django.db import models

# Create your models here.
class File(models.Model):
    filename = models.CharField(max_length=255)
    filesize = models.BigIntegerField()
    filetype = models.CharField(max_length=255)
    md5_hash = models.CharField(max_length=255)
    binary_image = models.FileField(upload_to='files')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Analysis(models.Model):
    result_classes = models.CharField(max_length=255)
    result_statistics = models.CharField(max_length=255)