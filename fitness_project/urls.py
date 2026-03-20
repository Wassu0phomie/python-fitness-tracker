"""
URL configuration for fitness_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
from main import views as main_views
from users import views as users_views

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),
    # Главная страница
    path('', main_views.welcome, name='welcome'),
    path('app/', include('main.urls')), #Не забыть изменить
    path('exercises/', include('exercises.urls')),
    path('users/', include('users.urls')),
]

# Для медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)