from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.create_plan_view, name='create_plan'),
    path('show/', views.plans_list_view, name='show_plan'),
    path('show/<int:pk>/', views.plan_detail_view, name='plan_detail'),
    path('archive/clear/', views.clear_archive_view, name='clear_archive'),
    path('delete/<int:pk>/', views.delete_plan_view, name='delete_plan'),
    path('active/clear/', views.clear_active_view, name='clear_active'),

]