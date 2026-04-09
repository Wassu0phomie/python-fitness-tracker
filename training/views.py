from exercises.models import Exercise
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import WorkoutPlan, WorkoutDay, DayExercise
from exercises.models import Exercise, MuscleGroup
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import date
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse


@login_required
def create_plan_view(request):
    """Создание плана тренировок - с поддержкой HTMX"""
    day_choices = WorkoutDay.DAYS_OF_WEEK
    exercises = Exercise.objects.filter(is_active=True)
    muscle_groups = MuscleGroup.objects.filter(is_group=True)

    if request.method == 'POST':
        # 1. Собираем все ID упражнений из всех выбранных дней
        selected_days = request.POST.getlist('selected_days')
        all_exercise_ids = []
        for day_num in selected_days:
            all_exercise_ids.extend(request.POST.getlist(f'exercises_{day_num}'))

        # 2. Очищаем список от пустых значений
        valid_exercises = [ex_id for ex_id in all_exercise_ids if ex_id]

        # 3. ГЛАВНАЯ ПРОВЕРКА: Если валидных упражнений 0 — возвращаем ошибку
        if not valid_exercises:
            context = {
                'day_choices': day_choices,
                'exercises': exercises,
                'muscle_groups': muscle_groups,
                'error': "План не может быть пустым. Добавьте хотя бы одно упражнение!"
            }

            if request.headers.get('HX-Request'):
                return render(request, 'training/partials/create_plan_content.html', context)
            return render(request, 'training/create_plan.html', context)

        title = request.POST.get('title')
        start_date = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        selected_days = request.POST.getlist('selected_days')

        # Конвертируем строку даты в объект даты Python
        end_date = date.fromisoformat(end_date_str)
        today = date.today()

        # ЛОГИКА ПРОВЕРКИ: Если дата окончания меньше сегодняшней, план создается неактивным
        is_active = True
        if end_date < today:
            is_active = False

        # Создаем План с учетом активности
        plan = WorkoutPlan.objects.create(
            user=request.user,
            title=title,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active
        )

        # Проходим по каждому выбранному дню
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
                    sets_value = sets_list[i] if i < len(sets_list) and sets_list[i] else 3
                    reps_value = reps_list[i] if i < len(reps_list) and reps_list[i] else 12

                    DayExercise.objects.create(
                        workout_day=workout_day,
                        exercise_id=exercise_ids[i],
                        sets=int(sets_value),
                        reps=int(reps_value),
                        order=i
                    )

        # HTMX запрос - редирект на детальную страницу
        if request.headers.get('HX-Request'):
            return redirect('plan_detail', pk=plan.pk)
        return redirect('plan_detail', pk=plan.pk)

    # GET запрос
    context = {
        'day_choices': day_choices,
        'exercises': exercises,
        'muscle_groups': muscle_groups,
    }


    if request.headers.get('HX-Request'):
        return render(request, 'training/partials/create_plan_content.html', context)
    return render(request, 'training/create_plan.html', context)


@login_required
def edit_plan_view(request, pk):
    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)

    if request.method == 'POST':
        # Проверяем, это реактивация или полное редактирование
        if 'reactivate' in request.POST:
            # Просто активируем план заново
            WorkoutPlan.objects.filter(pk=plan.pk).update(is_active=True)
            messages.success(request, f"План «{plan.title}» активирован!")
            return redirect('plan_detail', pk=plan.pk)

        # Полное редактирование плана
        title = request.POST.get('title')
        start_date = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        plan.title = title
        plan.start_date = start_date
        plan.end_date = end_date_str
        plan.is_active = True
        plan.save()

        # Удаляем старые дни и упражнения
        plan.days.all().delete()

        selected_days = request.POST.getlist('selected_days')

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
                    sets_value = 3
                    reps_value = 12

                    if i < len(sets_list) and sets_list[i]:
                        sets_value = int(sets_list[i])
                    if i < len(reps_list) and reps_list[i]:
                        reps_value = int(reps_list[i])

                    DayExercise.objects.create(
                        workout_day=workout_day,
                        exercise_id=exercise_ids[i],
                        sets=sets_value,
                        reps=reps_value,
                        order=i
                    )

        messages.success(request, f"План «{plan.title}» успешно обновлен!")
        return redirect('plan_detail', pk=plan.pk)

    # GET запрос - показываем форму редактирования
    existing_days = plan.days.all().prefetch_related('exercises__exercise')
    selected_day_numbers = [day.day_number for day in existing_days]

    context = {
        'plan': plan,
        'day_choices': WorkoutDay.DAYS_OF_WEEK,
        'exercises': Exercise.objects.filter(is_active=True),
        'muscle_groups': MuscleGroup.objects.filter(is_group=True),
        'existing_days': existing_days,
        'selected_day_numbers': selected_day_numbers,
    }

    return render(request, 'training/edit_plan.html', context)

@login_required
def plans_list_view(request):
    """Список планов - обертка"""
    from datetime import date

    WorkoutPlan.objects.filter(
        user=request.user,
        is_active=True,
        end_date__lt=timezone.now().date()
    ).update(is_active=False)

    today = date.today()
    all_plans = WorkoutPlan.objects.filter(user=request.user).order_by('-created_at')
    active_plans = all_plans.filter(is_active=True, end_date__gte=today)
    archive_plans = all_plans.exclude(id__in=active_plans.values_list('id', flat=True))

    context = {
        'active_plans': active_plans,
        'archive_plans': archive_plans,
        'active_count': active_plans.count(),
        'archive_count': archive_plans.count(),
        'today': today,
    }

    return render(request, 'training/plan_list.html', context)


@login_required
def plans_list_content(request):
    """HTMX контент списка планов"""
    WorkoutPlan.objects.filter(
        user=request.user,
        is_active=True,
        end_date__lt=timezone.now().date()
    ).update(is_active=False)

    today = date.today()
    all_plans = WorkoutPlan.objects.filter(user=request.user).order_by('-created_at')
    active_plans = all_plans.filter(is_active=True, end_date__gte=today)
    archive_plans = all_plans.exclude(id__in=active_plans.values_list('id', flat=True))

    filter_type = request.GET.get('filter', 'active')

    context = {
        'filter_type': filter_type,
        'active_plans': active_plans,
        'archive_plans': archive_plans,
        'active_count': active_plans.count(),
        'archive_count': archive_plans.count(),
        'today': today,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'training/partials/plan_list_content.html', context)
    return render(request, 'training/plan_list.html', context)

@login_required
def plan_detail_view(request, pk):
    """Детальная страница плана"""
    from progress.models import WorkoutLog

    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    days = plan.days.all().prefetch_related('exercises__exercise')

    now = timezone.localtime(timezone.now())
    today = now.date()
    current_day_num = now.isoweekday()
    is_completed_today = WorkoutLog.objects.filter(
        user=request.user,
        workout_day__plan=plan,
        completed_at__date=today
    ).exists()

    context = {
        'plan': plan,
        'days': days,
        'today_date': now,
        'current_day_num': current_day_num,
        'is_completed_today': is_completed_today,
    }

    return render(request, 'training/plan_detail.html', context)
@login_required
def plan_detail_content(request, pk):
    """HTMX контент детальной страницы плана"""
    from progress.models import WorkoutLog

    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    days = plan.days.all().prefetch_related('exercises__exercise')

    now = timezone.localtime(timezone.now())
    today = now.date()
    current_day_num = now.isoweekday()
    is_completed_today = WorkoutLog.objects.filter(
        user=request.user,
        workout_day__plan=plan,
        completed_at__date=today
    ).exists()

    context = {
        'plan': plan,
        'days': days,
        'today_date': timezone.now(),
        'current_day_num': current_day_num,
        'is_completed_today': is_completed_today,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'training/partials/plan_detail_content.html', context)
    return render(request, 'training/plan_detail.html', context)


@login_required
@require_POST
def clear_archive_view(request):
    """Очистка архива"""
    archived_plans = WorkoutPlan.objects.filter(user=request.user, is_active=False)
    count = archived_plans.count()

    if count > 0:
        archived_plans.delete()
        messages.success(request, f"Архив очищен: удалено {count} программ.")
    else:
        messages.info(request, "В архиве нет программ для удаления.")

    if request.headers.get('HX-Request'):
        return redirect('plans_list_content')
    return redirect('show_plan')


@login_required
@require_POST
def clear_active_view(request):
    """Очистка активных планов"""
    active_plans = WorkoutPlan.objects.filter(user=request.user, is_active=True)
    count = active_plans.count()

    if count > 0:
        active_plans.delete()
        messages.success(request, f"Все активные тренировки удалены ({count} шт.).")
    else:
        messages.info(request, "У вас нет активных тренировок.")

    if request.headers.get('HX-Request'):
        return redirect('plans_list_content')
    return redirect('show_plan')


@login_required
@require_POST
def delete_plan_view(request, pk):
    """Удаление плана"""
    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    title = plan.title
    plan.delete()

    messages.success(request, f"План «{title}» успешно удален.")

    if request.headers.get('HX-Request'):
        return HttpResponse("")
    return redirect('show_plan')


@login_required
@require_POST
def complete_workout_view(request, day_id):
    """Отметка выполнения тренировки (обычная)"""
    from progress.models import WorkoutLog

    day = get_object_or_404(WorkoutDay, id=day_id, plan__user=request.user)
    WorkoutLog.objects.create(user=request.user, workout_day=day)

    return HttpResponse("""
        <div class="alert alert-success rounded-pill py-3 px-4 border-0 shadow-sm" style="background: #D7FD51; color: #000;">
            <i class="bi bi-fire me-2"></i><b>ТРЕНИРОВКА ЗАЧТЕНА!</b>
        </div>
    """)


@login_required
def complete_workout_htmx(request, day_id):
    """HTMX отметка выполнения тренировки"""
    from progress.models import WorkoutLog

    day = get_object_or_404(WorkoutDay, id=day_id, plan__user=request.user)
    WorkoutLog.objects.get_or_create(user=request.user, workout_day=day)

    # Возвращаем обновленный блок дня
    return render(request, 'training/partials/day_card_detail.html', {'day': day})


@login_required
def htmx_add_day(request):
    """HTMX: Возвращает блок для нового тренировочного дня"""
    day_num = request.GET.get('day_num')
    day_label = request.GET.get('label')

    html = f'''
    <div class="card mb-4 border-0 bg-light p-4 rounded-4 shadow-sm htmx-fade-in" id="day-block-{day_num}">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-bold mb-0 text-uppercase">{day_label}</h5>
            <button type="button" class="btn-close" onclick="removeDayBlock({day_num})"></button>
        </div>

        <div class="exercise-list" id="exercise-list-{day_num}"></div>

        <button type="button"
                class="btn btn-link text-dark fw-bold text-decoration-none p-0 mt-2 open-gallery-btn"
                data-bs-toggle="modal"
                data-bs-target="#exerciseGallery"
                data-day="{day_num}">
            <i class="bi bi-plus-circle-fill me-2"></i>Добавить упражнение
        </button>
    </div>
    '''

    return HttpResponse(html)


@login_required
def search_exercises_htmx(request):
    """HTMX: Поиск упражнений для модалки"""
    query = request.GET.get('q', '').lower()
    muscle_slug = request.GET.get('muscle', 'all')

    exercises = Exercise.objects.filter(is_active=True)

    if query:
        exercises = exercises.filter(name__icontains=query)

    if muscle_slug != 'all':
        exercises = exercises.filter(muscle_groups__slug=muscle_slug)

    exercises = exercises[:20]

    html = ''
    for ex in exercises:
        primary_muscles = ex.primary_muscles.all()[:2]
        muscles_html = ''.join([
            f'<span class="badge bg-light text-muted" style="font-size: 0.55rem;">{m.name}</span>'
            for m in primary_muscles
        ])

        html += f'''
        <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm-hover cursor-pointer p-2"
                 style="border-radius: 15px; transition: 0.3s; cursor: pointer;"
                 onclick="addExerciseToDay('{ex.id}', '{ex.name}')">
                <div class="text-center mb-2">
                    <img src="{ex.main_image}" class="img-fluid rounded" 
                         style="height: 100px; object-fit: contain;"
                         onerror="this.src='https://via.placeholder.com/100?text=No+Image'">
                </div>
                <div class="text-center">
                    <h6 class="small fw-bold mb-0">{ex.name}</h6>
                    <div class="mt-1">
                        {muscles_html}
                    </div>
                </div>
            </div>
        </div>
        '''

    if not exercises:
        html = '<div class="col-12 text-center text-muted py-5"><i class="bi bi-emoji-frown display-4"></i><p class="mt-3">Упражнения не найдены</p></div>'

    return HttpResponse(html)


@login_required
@require_POST
def clear_active_htmx(request):
    """HTMX очистка активных планов"""
    active_plans = WorkoutPlan.objects.filter(user=request.user, is_active=True)
    active_plans.delete()
    return HttpResponse("")


@login_required
@require_POST
def clear_archive_htmx(request):
    """HTMX очистка архива"""
    from datetime import date
    today = date.today()
    archived_plans = WorkoutPlan.objects.filter(
        user=request.user,
        is_active=False
    ) | WorkoutPlan.objects.filter(
        user=request.user,
        end_date__lt=today
    )
    archived_plans.delete()
    return HttpResponse("")


@login_required
@require_POST
def delete_plan_htmx(request, pk):
    """HTMX удаление плана без перезагрузки"""
    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    plan.delete()
    return HttpResponse("")