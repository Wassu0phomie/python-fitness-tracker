from django.db import models
from django.utils.text import slugify


class MuscleGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Группа мышц"
        verbose_name_plural = "Группы мышц"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Exercise(models.Model):
    TYPE_CHOICES = [
        ('strength', 'Силовое'),
        ('cardio', 'Кардио'),
        ('flexibility', 'Растяжка'),
        ('balance', 'Баланс'),
        ('warmup', 'Разминка'),
        ('cooldown', 'Заминка'),
    ]

    DIFFICULTY_CHOICES = [
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
        ('expert', 'Эксперт'),
    ]

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    instructions = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    precautions = models.TextField(blank=True)

    exercise_type = models.CharField(max_length=20, choices=TYPE_CHOICES,
                                     default='strength')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES,
                                  default='beginner')

    primary_muscles = models.ManyToManyField(MuscleGroup,
                                             related_name='primary_exercises')
    secondary_muscles = models.ManyToManyField(MuscleGroup,
                                               related_name='secondary_exercises',
                                               blank=True)
    equipment = models.ManyToManyField(Equipment, blank=True)

    video_url = models.URLField(blank=True)
    video_file = models.FileField(upload_to='exercise_videos/', blank=True, null=True)
    image = models.ImageField(upload_to='exercise_images/', blank=True, null=True)

    calories_per_hour = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Упражнение"
        verbose_name_plural = "Упражнения"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['exercise_type']),
            models.Index(fields=['difficulty']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def main_image(self):
        return self.image.url if self.image else None


# class FavoriteExercise(models.Model):
#     from apps.users.models import CustomUser
#
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
#                              related_name='favorite_exercises')
#     exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
#     added_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         unique_together = ['user', 'exercise']
#         verbose_name = "Избранное упражнение"
#         verbose_name_plural = "Избранные упражнения"
#         ordering = ['-added_at']
#
#     def __str__(self):
#         return f"{self.user.email} - {self.exercise.name}"