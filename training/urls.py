from django.urls import path
from . import views

urlpatterns = [
    # Основные страницы (обертки)
    path('new/', views.create_plan_view, name='create_plan'),
    path('show/', views.plans_list_view, name='show_plan'),
    path('show/<int:pk>/', views.plan_detail_view, name='plan_detail'),
    path('plan/<int:pk>/edit/', views.edit_plan_view, name='edit_plan'),

    # HTMX контент (partials)
    path('htmx/create-plan-content/', views.create_plan_view, name='create_plan_content'),
    path('htmx/edit-plan-content/<int:pk>/', views.edit_plan_view, name='edit_plan_content'),
    path('htmx/plans-list-content/', views.plans_list_content, name='plans_list_content'),
    path('htmx/plan-detail-content/<int:pk>/', views.plan_detail_content, name='plan_detail_content'),

    # HTMX динамические компоненты
    path('htmx/add-day/', views.htmx_add_day, name='htmx_add_day'),
    path('htmx/search-exercises/', views.search_exercises_htmx, name='search_exercises_htmx'),
    path('htmx/complete-workout/<int:day_id>/', views.complete_workout_htmx, name='complete_workout_htmx'),

    # Действия (POST)
    path('archive/clear/', views.clear_archive_view, name='clear_archive'),
    path('delete/<int:pk>/', views.delete_plan_view, name='delete_plan'),
    path('active/clear/', views.clear_active_view, name='clear_active'),
    path('complete-workout/<int:day_id>/', views.complete_workout_view, name='complete_workout'),

    # HTMX действия (без перезагрузки)
    path('htmx/delete-plan/<int:pk>/', views.delete_plan_htmx, name='delete_plan_htmx'),
    path('htmx/clear-active/', views.clear_active_htmx, name='clear_active_htmx'),
    path('htmx/clear-archive/', views.clear_archive_htmx, name='clear_archive_htmx'),
]