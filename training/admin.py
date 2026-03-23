from django.contrib import admin
from .models import WorkoutPlan, WorkoutDay, DayExercise


# Таблица упражнений, которая будет "встроена" в карточку дня
class DayExerciseInline(admin.TabularInline):
    model = DayExercise
    extra = 1  # Одно пустое поле для быстрого добавления нового упражнения
    fields = ('exercise', 'sets', 'reps', 'order')
    sortable_field_name = "order"  # Позволяет задавать порядок выполнения


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    # 1. Показываем название плана и пользователя прямо в списке
    list_display = ('get_day_name', 'get_plan_title', 'get_user_name', 'exercises_count')

    # 2. Добавляем фильтры справа (это самое важное!)
    # Теперь вы сможете кликнуть на "План: Набор массы" и увидеть только его дни
    list_filter = ('day_number', 'plan__user', 'plan__title')

    # 3. Добавляем поиск
    search_fields = ('plan__title', 'plan__user__username')

    inlines = [DayExerciseInline]

    # Вспомогательные методы для отображения данных из связанных таблиц
    def get_day_name(self, obj):
        return obj.get_day_number_display()

    get_day_name.short_description = "День недели"

    def get_plan_title(self, obj):
        return obj.plan.title

    get_plan_title.short_description = "План"

    def get_user_name(self, obj):
        return obj.plan.user.username

    get_user_name.short_description = "Пользователь"

    def exercises_count(self, obj):
        return obj.exercises.count()

    exercises_count.short_description = "Упр-й"


# Также зарегистрируем План, чтобы видеть в нем список дней
class WorkoutDayInline(admin.StackedInline):
    model = WorkoutDay
    extra = 0
    show_change_link = True  # Ссылка "Изменить", которая ведет сразу к упражнениям дня


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_active', 'start_date', 'end_date')
    inlines = [WorkoutDayInline]

