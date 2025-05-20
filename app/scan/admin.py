from django.contrib import admin
from .models import AnalysisResult

# Register your models here.
@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'filename')
    ordering = ('-created_at',)