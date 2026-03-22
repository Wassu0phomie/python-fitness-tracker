from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import WorkoutDay  # Чтобы получить список дней для кнопок


@login_required
def create_plan_view(request):
    # Передаем список дней (ПН-ВС) из модели, чтобы циклом отрисовать кнопки
    day_choices = WorkoutDay.DAYS_OF_WEEK

    return render(request, 'training/create_plan.html', {
        'day_choices': day_choices
    })