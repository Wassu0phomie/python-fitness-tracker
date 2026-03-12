from django.db import models
from django.conf import settings
from exercises.models import Exercise

class WorkoutPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Название плана")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class WorkoutDay(models.Model):
    plan = models.ForeignKey(WorkoutPlan, related_name='days', on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField(verbose_name="День недели (1-7)")

    class Meta:
        unique_together = ('plan', 'day_number')
        ordering = ['day_number']

class DayExercise(models.Model):
    workout_day = models.ForeignKey(WorkoutDay, related_name='exercises', on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets_reps = models.CharField(max_length=100, verbose_name="Подходы и повторения")