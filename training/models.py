from django.db import models
from django.conf import settings
from exercises.models import Exercise
from datetime import date
from django.core.validators import MinValueValidator


class WorkoutPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Название плана")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")

    is_active = models.BooleanField(default=True, verbose_name="Активен")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    # НОВОЕ: Метод для проверки просрочки
    @property
    def is_expired(self):
        return date.today() > self.end_date


class WorkoutDay(models.Model):
    # НОВОЕ: Список для кнопок
    DAYS_OF_WEEK = [
        (1, 'ПН'), (2, 'ВТ'), (3, 'СР'), (4, 'ЧТ'), (5, 'ПТ'), (6, 'СБ'), (7, 'ВС'),
    ]

    plan = models.ForeignKey(WorkoutPlan, related_name='days', on_delete=models.CASCADE)
    # ИЗМЕНЕНО: добавили choices
    day_number = models.PositiveIntegerField(choices=DAYS_OF_WEEK, verbose_name="День недели")

    class Meta:
        unique_together = ('plan', 'day_number')
        ordering = ['day_number']


class DayExercise(models.Model):
    workout_day = models.ForeignKey(WorkoutDay, related_name='exercises', on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    # Устанавливаем минимальное значение 1 для подходов
    sets = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Подходы"
    )

    # Меняем CharField на PositiveIntegerField для строгой числовой логики
    reps = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Повторения"
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Упражнение в тренировке"
        verbose_name_plural = "Упражнения в тренировках"