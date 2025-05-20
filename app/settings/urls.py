from django.urls import path

from . import views

urlpatterns = [
    path('', views.profile, name='profile'),
    path('manage', views.admin_view, name='manage'),
    path('manage/promote/<int:user_id>', views.promote, name='promote'),
    path('manage/demote/<int:user_id>', views.demote, name='demote'),
]