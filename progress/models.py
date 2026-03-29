from django.db import models
from django.conf import settings
from training.models import WorkoutDay, DayExercise

class WorkoutLog(models.Model):
    # Вместо User используй settings.AUTH_USER_MODEL
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']

class ProgressEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='progress_photos/%Y/%m/', null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    comment = models.TextField(max_length=500, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']