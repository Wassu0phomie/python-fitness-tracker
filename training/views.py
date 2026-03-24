from exercises.models import Exercise  # Импортируй свою модель упражнений
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import WorkoutPlan, WorkoutDay, DayExercise
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import date
from django.contrib import messages
@login_required
def create_plan_view(request):
    if request.method == 'POST':
        # 1. Собираем все ID упражнений из всех выбранных дней
        selected_days = request.POST.getlist('selected_days')
        all_exercise_ids = []
        for day_num in selected_days:
            all_exercise_ids.extend(request.POST.getlist(f'exercises_{day_num}'))

        # 2. Очищаем список от пустых значений (если пользователь добавил строку, но не выбрал упражнение)
        valid_exercises = [ex_id for ex_id in all_exercise_ids if ex_id]

        # 3. ГЛАВНАЯ ПРОВЕРКА: Если валидных упражнений 0 — возвращаем ошибку
        if not valid_exercises:
            day_choices = WorkoutDay.DAYS_OF_WEEK
            exercises = Exercise.objects.all()
            return render(request, 'training/create_plan.html', {
                'day_choices': day_choices,
                'exercises': exercises,
                'error': "План не может быть пустым. Добавьте хотя бы одно упражнение!"
            })

        title = request.POST.get('title')
        start_date = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        selected_days = request.POST.getlist('selected_days')

        # Конвертируем строку даты в объект даты Python
        end_date = date.fromisoformat(end_date_str)
        today = date.today()

        # ЛОГИКА ПРОВЕРКИ:
        # Если дата окончания меньше сегодняшней, план создается неактивным
        is_active = True
        if end_date < today:
            is_active = False

        # Создаем План с учетом активности
        plan = WorkoutPlan.objects.create(
            user=request.user,
            title=title,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active  # Передаем результат проверки
        )

        # 2. Проходим по каждому выбранному дню (код без изменений)
        for day_num in selected_days:
            workout_day = WorkoutDay.objects.create(
                plan=plan,
                day_number=day_num
            )

            exercise_ids = request.POST.getlist(f'exercises_{day_num}')
            sets_list = request.POST.getlist(f'sets_{day_num}')
            reps_list = request.POST.getlist(f'reps_{day_num}')

            for i in range(len(exercise_ids)):
                if exercise_ids[i]:
                    DayExercise.objects.create(
                        workout_day=workout_day,
                        exercise_id=exercise_ids[i],
                        sets=sets_list[i] if sets_list[i] else 0,
                        reps=reps_list[i] if reps_list[i] else "0",
                        order=i
                    )

        return redirect('plan_detail', pk=plan.pk)

    day_choices = WorkoutDay.DAYS_OF_WEEK
    exercises = Exercise.objects.all()
    return render(request, 'training/create_plan.html', {
        'day_choices': day_choices,
        'exercises': exercises
    })


@login_required
def plans_list_view(request):
    WorkoutPlan.objects.filter(
        user=request.user,
        is_active=True,
        end_date__lt=timezone.now().date()
    ).update(is_active=False)
    # Получаем все планы именно этого пользователя
    # Сортируем: сначала новые (-created_at)
    all_plans = WorkoutPlan.objects.filter(user=request.user).order_by('-created_at')

    # Фильтруем активные (флаг is_active и дата окончания еще не наступила)
    active_plans = all_plans.filter(is_active=True, end_date__gte=timezone.now().date())

    # Все остальные уходят в архив
    archive_plans = all_plans.exclude(id__in=active_plans.values_list('id', flat=True))

    context = {
        'active_plans': active_plans,
        'archive_plans': archive_plans,
    }
    return render(request, 'training/plan_list.html', context)


def plan_detail_view(request, pk):
    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    days = plan.days.all().prefetch_related('exercises__exercise')

    # Получаем текущий день недели (0 - Понедельник, 1 - Вторник и т.д.)
    current_day_num = timezone.now().isoweekday()

    # Маппинг для твоей модели (если у тебя ПН=1, СР=3 и т.д., скорректируй числа)
    # Python: 0=ПН, 1=ВТ, 2=СР, 3=ЧТ, 4=ПТ, 5=СБ, 6=ВС
    # Допустим, в твоей модели числа совпадают (1-7 или 0-6)

    return render(request, 'training/plan_detail.html', {
        'plan': plan,
        'days': days,
        'today_date': timezone.now(),
        'current_day_num': current_day_num  # Передаем в шаблон

    })


@login_required
@require_POST
def clear_archive_view(request):
    """Удаляет только архивные (неактивные) планы пользователя"""
    archived_plans = WorkoutPlan.objects.filter(user=request.user, is_active=False)
    count = archived_plans.count()

    if count > 0:
        archived_plans.delete()
        messages.success(request, f"Архив очищен: удалено {count} программ.")
    else:
        messages.info(request, "В архиве нет программ для удаления.")

    return redirect('show_plan')


@login_required
@require_POST
def clear_active_view(request):
    """Удаляет все текущие активные планы пользователя"""
    active_plans = WorkoutPlan.objects.filter(user=request.user, is_active=True)
    count = active_plans.count()

    if count > 0:
        active_plans.delete()
        messages.success(request, f"Все активные тренировки удалены ({count} шт.).")
    else:
        messages.info(request, "У вас нет активных тренировок.")

    return redirect('show_plan')


@login_required
@require_POST
def delete_plan_view(request, pk):
    # Ищем план, принадлежащий именно текущему пользователю
    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    title = plan.title
    plan.delete()

    messages.success(request, f"План «{title}» успешно удален.")
    return redirect('show_plan')