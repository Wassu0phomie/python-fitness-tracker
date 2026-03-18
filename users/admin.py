from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProgress

# Настройка отображения пользователей
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # Какие колонки видеть в таблице
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    # По каким полям искать
    search_fields = ('email', 'first_name', 'last_name')
    # Фильтры справа
    list_filter = ('is_staff', 'is_active')

# Настройка отображения прогресса
@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight', 'height', 'bmi', 'date_recorded')