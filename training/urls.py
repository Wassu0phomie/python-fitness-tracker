from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.create_plan_view, name='create_plan'),
    path('show/', views.plans_list_view, name='show_plan'),
    path('show/<int:pk>/', views.plan_detail_view, name='plan_detail'),
    path('archive/clear/', views.clear_archive_view, name='clear_archive'),
    path('delete/<int:pk>/', views.delete_plan_view, name='delete_plan'),
    path('active/clear/', views.clear_active_view, name='clear_active'),
    path('plan/<int:pk>/edit/', views.edit_plan_view, name='edit_plan'),
    path('complete-workout/<int:day_id>/', views.complete_workout_view, name='complete_workout'),

    # HTMX endpoints
    path('htmx/add-day/', views.htmx_add_day, name='htmx_add_day'),
    path('htmx/search-exercises/', views.search_exercises_htmx, name='search_exercises_htmx'),

    path('plans/partial/', views.plans_list_partial, name='plans_list_partial'),
    path('plans/delete-htmx/<int:pk>/', views.delete_plan_htmx, name='delete_plan_htmx'),
    path('plans/clear-active-htmx/', views.clear_active_htmx, name='clear_active_htmx'),
    path('plans/clear-archive-htmx/', views.clear_archive_htmx, name='clear_archive_htmx'),
]