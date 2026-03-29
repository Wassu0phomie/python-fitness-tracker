from django.urls import path
from . import views

urlpatterns = [
    path('', views.progress_view, name='progress'),
    path('upload/', views.upload_progress_htmx, name='upload_progress'),
    path('delete/<int:photo_id>/', views.delete_photo_htmx, name='delete_photo'),
]