from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('delete-result/<int:result_id>', views.delete_result, name='delete_result'),
]