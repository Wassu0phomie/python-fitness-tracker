from django.contrib import admin
from .models import WorkoutPlan, WorkoutDay, DayExercise


# 1. Упражнения внутри Дня
class DayExerciseInline(admin.TabularInline):
    model = DayExercise
    extra = 1  # Количество пустых полей для новых упражнений
    fields = ('exercise', 'sets', 'reps', 'order')
    sortable_field_name = "order"


# 2. Дни внутри Плана
class WorkoutDayInline(admin.StackedInline):
    model = WorkoutDay
    extra = 1
    show_change_link = True  # Позволяет перейти к редактированию конкретного дня


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'user', 'start_date')
    search_fields = ('title', 'user__username')
    inlines = [WorkoutDayInline]

    # Раскрасим статус "Активен" в списке
    list_editable = ('is_active',)


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    list_display = ('day_number', 'plan', 'get_user')
    list_filter = ('day_number', 'plan__user')
    inlines = [DayExerciseInline]

    def get_user(self, obj):
        return obj.plan.user

    get_user.short_description = 'Пользователь'


@admin.register(DayExercise)
class DayExerciseAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'workout_day', 'sets', 'reps')
    list_filter = ('workout_day__plan__user', 'exercise')