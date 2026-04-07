from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExerciseListView.as_view(), name='exercise_list'),
    path('<slug:slug>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('htmx/load-more/', views.htmx_load_more_exercises, name='htmx_load_more_exercises'),

]