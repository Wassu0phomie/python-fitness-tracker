from django.contrib import admin
from django.utils.html import format_html
from .models import Equipment, MuscleGroup, Exercise


# ========== РЕГИСТРАЦИЯ МОДЕЛЕЙ В АДМИНКЕ ==========

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Админка для оборудования"""
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug')
        }),
    )


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    """Админка для групп мышц"""
    list_display = ['name', 'slug', 'icon']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'icon', 'description')
        }),
    )


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """Админка для упражнений"""

    # Отображение в списке - только реальные поля модели
    list_display = [
        'name',
        'slug',
        'exercise_type',  # Используем реальное поле
        'difficulty',  # Используем реальное поле
        'is_active',
        'created_at'
    ]

    # Фильтры
    list_filter = [
        'exercise_type',
        'difficulty',
        'is_active',
        'created_at'
    ]

    # Поиск
    search_fields = [
        'name',
        'description',
        'instructions',
        'benefits',
        'precautions'
    ]

    # Автозаполнение полей ManyToMany
    autocomplete_fields = ['primary_muscles', 'secondary_muscles', 'equipment']

    # Предварительное заполнение slug
    prepopulated_fields = {'slug': ('name',)}

    # Разделение на группы полей (fieldsets)
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name',
                'slug',
                'description',
            )
        }),
        ('Тип и сложность', {
            'fields': (
                'exercise_type',
                'difficulty',
            )
        }),
        ('Детальное описание', {
            'fields': (
                'instructions',
                'benefits',
                'precautions',
            ),
            'classes': ('collapse',)  # Сворачиваемая секция
        }),
        ('Медиа файлы', {
            'fields': (
                'image',
                'video_file',
                'video_url'
            )
        }),
        ('Классификация', {
            'fields': (
                'primary_muscles',
                'secondary_muscles',
                'equipment'
            )
        }),
        ('Дополнительно', {
            'fields': (
                'calories_per_hour',
                'is_active'
            )
        }),
    )

    # Поля только для чтения - только реальные поля
    readonly_fields = ['created_at', 'updated_at']
