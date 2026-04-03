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
    # Теперь в списке сразу будет видно галочку
    list_display = ['name', 'is_group', 'slug', 'icon']

    # Можно быстро отфильтровать только группы или только мышцы
    list_filter = ['is_group']

    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'is_group', 'slug', 'icon', 'description')
        }),
    )


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """Админка для упражнений с разделением на общие группы и детальные мышцы"""

    list_display = [
        'name',
        'display_muscle_groups',  # Добавим отображение групп в список
        'exercise_type',
        'difficulty',
        'is_active',
    ]

    # Добавляем фильтр по новым общим группам
    list_filter = [
        'muscle_groups',
        'exercise_type',
        'difficulty',
        'is_active',
    ]

    search_fields = ['name', 'description']

    # ВАЖНО: Добавляем muscle_groups в автозаполнение
    # Теперь у вас будет 3 удобных окна поиска мышц
    autocomplete_fields = [
        'muscle_groups',
        'primary_muscles',
        'secondary_muscles',
        'equipment'
    ]

    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Тип и сложность', {
            'fields': ('exercise_type', 'difficulty')
        }),
        ('Классификация (АНАТОМИЯ)', {
            'fields': (
                'muscle_groups',     # Общая категория (например: Плечи)
                'primary_muscles',   # Детальные основные (например: Передняя дельта)
                'secondary_muscles', # Вспомогательные (например: Трицепс)
                'equipment'
            ),
            'description': 'Сначала выберите общую группу для фильтрации, затем детальные мышцы.'
        }),
        ('Медиа файлы', {
            'fields': ('image', 'video_file', 'image_url', 'video_url')
        }),
        ('Текстовые блоки', {
            'fields': ('instructions', 'benefits', 'precautions'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('calories_per_hour', 'is_active', 'created_at', 'updated_at')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    # Вспомогательный метод для красивого списка
    def display_muscle_groups(self, obj):
        return ", ".join([m.name for m in obj.muscle_groups.all()])
    display_muscle_groups.short_description = 'Целевые группы'
