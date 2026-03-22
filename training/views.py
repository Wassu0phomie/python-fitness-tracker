from exercises.models import Exercise  # Импортируй свою модель упражнений
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import WorkoutPlan, WorkoutDay, DayExercise


@login_required
def create_plan_view(request):
    if request.method == 'POST':
        # 1. Получаем основные данные плана
        title = request.POST.get('title')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        selected_days = request.POST.getlist('selected_days') # Список ID дней (1, 2, 3...)

        # Создаем сам План
        plan = WorkoutPlan.objects.create(
            user=request.user,
            title=title,
            start_date=start_date,
            end_date=end_date
        )

        # 2. Проходим по каждому выбранному дню
        for day_num in selected_days:
            workout_day = WorkoutDay.objects.create(
                plan=plan,
                day_number=day_num
            )

            # Извлекаем списки упражнений, сетов и репсов именно для ЭТОГО дня
            # В HTML мы давали им имена типа exercises_1, sets_1 и т.д.
            exercise_ids = request.POST.getlist(f'exercises_{day_num}')
            sets_list = request.POST.getlist(f'sets_{day_num}')
            reps_list = request.POST.getlist(f'reps_{day_num}')

            # 3. Создаем упражнения для этого дня
            for i in range(len(exercise_ids)):
                if exercise_ids[i]: # Проверяем, что упражнение выбрано
                    DayExercise.objects.create(
                        workout_day=workout_day,
                        exercise_id=exercise_ids[i],
                        sets=sets_list[i] if sets_list[i] else 0,
                        reps=reps_list[i] if reps_list[i] else "0",
                        order=i
                    )

        return redirect('index') # После сохранения летим на главную

    # Если это GET запрос — просто показываем пустую форму
    day_choices = WorkoutDay.DAYS_OF_WEEK
    exercises = Exercise.objects.all()
    return render(request, 'training/create_plan.html', {
        'day_choices': day_choices,
        'exercises': exercises
    })