import os
import django

# 1. Сначала устанавливаем переменную окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_project.settings')

# 2. Затем инициализируем Django
django.setup()

# 3. И ТОЛЬКО ТЕПЕРЬ импортируем модели
from exercises.models import MuscleGroup, Equipment

# Группы мышц
muscles = [
    "Грудные", "Широчайшие", "Трапеции", "Поясница",
    "Передняя дельта", "Средняя дельта", "Задняя дельта",
    "Бицепс", "Трицепс", "Предплечья",
    "Квадрицепс", "Бицепс бедра", "Ягодицы", "Икры",
    "Пресс", "Косые мышцы живота"
]

for name in muscles:
    MuscleGroup.objects.get_or_create(name=name)

# Оборудование
equip_list = [
    "Собственный вес", "Штанга", "Гантели", "Гиря",
    "Турник", "Брусья", "Скамья", "Стойки",
    "Кроссовер", "Тренажер Смита", "Фитнес-резинки", "TRX"
]

for name in equip_list:
    Equipment.objects.get_or_create(name=name)

print("База данных успешно наполнена основными группами и оборудованием!")