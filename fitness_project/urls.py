"""
URL configuration for fitness_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),
    # Главная страница
    path('', include('main.urls')),

    path('exercises/', include('exercises.urls')),
]

# Для медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)