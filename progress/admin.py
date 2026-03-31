from django.contrib import admin
from .models import WorkoutLog, ProgressEntry


@admin.register(ProgressEntry)
class ProgressEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'weight', 'created_at')
    # Добавляем в readonly_fields, чтобы Django не ругался на нередактируемое поле
    readonly_fields = ('created_at',)

    # Убираем created_at из основного списка редактируемых полей,
    # либо оставляем только в readonly
    fields = ('user', 'image', 'weight', 'comment', 'created_at')


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'workout_day', 'completed_at')
    list_filter = ('user', 'completed_at')