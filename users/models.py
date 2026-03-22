from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен для регистрации")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # Логин только по Email
    email = models.EmailField('Email адрес', unique=True)

    avatar = models.ImageField(
        'Фото профиля',
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True
    )
    # Основные данные
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)

    # Спортивные/Личные данные
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    GENDER_CHOICES = [('M', 'Мужской'), ('F', 'Женский')]
    gender = models.CharField('Пол', max_length=1, choices=GENDER_CHOICES, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email


class UserProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress_logs'
    )

    # Физические показатели
    weight = models.FloatField(
        'Вес (кг)',
        validators=[MinValueValidator(20.0), MaxValueValidator(300.0)]
    )
    height = models.FloatField(
        'Рост (см)',
        validators=[MinValueValidator(50.0), MaxValueValidator(250.0)]
    )

    # Системные поля
    date_recorded = models.DateTimeField('Дата записи', auto_now_add=True)

    class Meta:
        ordering = ['-date_recorded']  # Последние записи всегда сверху
        verbose_name = 'Прогресс пользователя'
        verbose_name_plural = 'История прогресса'

    def __str__(self):
        return f"{self.user.email} - {self.date_recorded.strftime('%d.%m.%Y')} ({self.weight} кг)"

    @property
    def bmi(self):
        """Автоматический расчет Индекса Массы Тела (ИМТ)"""
        if self.height > 0:
            # Формула: вес / (рост в метрах ^ 2)
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters ** 2), 1)
        return 0