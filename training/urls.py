from django.urls import path
from . import views

urlpatterns = [
    path('plan/new/', views.create_plan_view, name='create_plan'),
]