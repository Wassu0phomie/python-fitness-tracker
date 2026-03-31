from django.urls import path
from . import views

urlpatterns = [
    # ... ваши старые пути (progress, upload и т.д.) ...
    path('recipes/', views.recipe_list, name='recipe_list'),
]