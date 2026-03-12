from django.urls import path
from .views import ExerciseListView, ExerciseDetailView, ExerciseSearchView

urlpatterns = [
    path('', ExerciseListView.as_view(), name='exercise_list'),
    path('search/', ExerciseSearchView.as_view(), name='exercise_search'),
    path('<slug:slug>/', ExerciseDetailView.as_view(), name='exercise_detail'),
]