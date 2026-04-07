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


@login_required
def create_plan_view(request):
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
            day_choices = WorkoutDay.DAYS_OF_WEEK
            exercises = Exercise.objects.filter(is_active=True)
            muscle_groups = MuscleGroup.objects.all()
            return render(request, 'training/create_plan.html', {
                'day_choices': day_choices,
                'exercises': exercises,
                'muscle_groups': muscle_groups,
                'error': "План не может быть пустым. Добавьте хотя бы одно упражнение!"
            })

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
                    # Безопасное получение значений с проверкой длины списков
                    sets_value = sets_list[i] if i < len(sets_list) and sets_list[i] else 3
                    reps_value = reps_list[i] if i < len(reps_list) and reps_list[i] else 12

                    DayExercise.objects.create(
                        workout_day=workout_day,
                        exercise_id=exercise_ids[i],
                        sets=int(sets_value),
                        reps=int(reps_value),
                        order=i
                    )

        return redirect('plan_detail', pk=plan.pk)

    day_choices = WorkoutDay.DAYS_OF_WEEK
    exercises = Exercise.objects.filter(is_active=True)
    muscle_groups = MuscleGroup.objects.all()
    return render(request, 'training/create_plan.html', {
        'day_choices': day_choices,
        'exercises': exercises,
        'muscle_groups': muscle_groups
    })

@login_required
def plans_list_view(request):
    WorkoutPlan.objects.filter(
        user=request.user,
        is_active=True,
        end_date__lt=timezone.now().date()
    ).update(is_active=False)

    all_plans = WorkoutPlan.objects.filter(user=request.user).order_by('-created_at')
    active_plans = all_plans.filter(is_active=True, end_date__gte=timezone.now().date())
    archive_plans = all_plans.exclude(id__in=active_plans.values_list('id', flat=True))

    context = {
        'active_plans': active_plans,
        'archive_plans': archive_plans,
    }
    return render(request, 'training/plan_list.html', context)


def plan_detail_view(request, pk):
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

    return render(request, 'training/plan_detail.html', {
        'plan': plan,
        'days': days,
        'today_date': timezone.now(),
        'current_day_num': current_day_num,
        'is_completed_today': is_completed_today,
    })


@login_required
@require_POST
def clear_archive_view(request):
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
    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    title = plan.title
    plan.delete()

    messages.success(request, f"План «{title}» успешно удален.")
    return redirect('show_plan')


@login_required
def edit_plan_view(request, pk):
    # Получаем план, принадлежащий именно этому пользователю
    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)

    if request.method == 'POST':
        # Логика сохранения
        plan.title = request.POST.get('title')
        plan.start_date = request.POST.get('start_date')
        plan.end_date = request.POST.get('end_date')
        plan.is_active = True
        plan.save()

        # Удаляем старые дни и упражнения, чтобы перезаписать их новыми
        plan.days.all().delete()

        selected_days = request.POST.getlist('selected_days')

        for day_num in selected_days:
            workout_day = WorkoutDay.objects.create(plan=plan, day_number=day_num)

            exercise_ids = request.POST.getlist(f'exercises_{day_num}')
            sets_list = request.POST.getlist(f'sets_{day_num}')
            reps_list = request.POST.getlist(f'reps_{day_num}')

            # Безопасное создание упражнений с проверкой длины списков
            for i in range(len(exercise_ids)):
                if exercise_ids[i]:
                    # Проверяем, что индекс существует в списках
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

        messages.success(request, f"План «{plan.title}» успешно обновлен и активирован!")
        return redirect('plan_detail', pk=plan.pk)

    # Для GET-запроса: подготавливаем данные
    day_choices = WorkoutDay.DAYS_OF_WEEK
    exercises = Exercise.objects.filter(is_active=True)
    muscle_groups = MuscleGroup.objects.all()

    # Получаем уже выбранные дни и упражнения для JS
    existing_days = plan.days.all().prefetch_related('exercises__exercise')

    return render(request, 'training/edit_plan.html', {
        'plan': plan,
        'day_choices': day_choices,
        'exercises': exercises,
        'muscle_groups': muscle_groups,
        'existing_days': existing_days,
    })


@login_required
@require_POST
def complete_workout_view(request, day_id):
    from progress.models import WorkoutLog
    from .models import WorkoutDay

    day = get_object_or_404(WorkoutDay, id=day_id, plan__user=request.user)
    WorkoutLog.objects.create(user=request.user, workout_day=day)

    return HttpResponse("""
        <div class="alert alert-success rounded-pill py-3 px-4 border-0 shadow-sm" style="background: #D7FD51; color: #000;">
            <i class="bi bi-fire me-2"></i><b>ТРЕНИРОВКА ЗАЧТЕНА!</b>
        </div>
    """)


# ========== HTMX FUNCTIONS ==========

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
def complete_workout_htmx(request, day_id):
    """HTMX отметка выполнения тренировки"""
    from progress.models import WorkoutLog

    day = get_object_or_404(WorkoutDay, id=day_id, plan__user=request.user)
    WorkoutLog.objects.get_or_create(user=request.user, workout_day=day)

    # Возвращаем обновленную карточку дня
    return render(request, 'training/partials/day_card_detail.html', {'day': day})


# training/views.py - добавьте в самый конец файла

def plans_list_partial(request):
    """HTMX версия списка планов с оригинальным видом"""
    from datetime import date
    today = date.today()

    filter_type = request.GET.get('filter', 'active')

    all_plans = WorkoutPlan.objects.filter(user=request.user).order_by('-created_at')
    active_plans = all_plans.filter(is_active=True, end_date__gte=today)
    archive_plans = all_plans.exclude(id__in=active_plans.values_list('id', flat=True))

    context = {
        'filter_type': filter_type,
        'active_plans': active_plans if filter_type == 'active' else [],
        'archive_plans': archive_plans if filter_type == 'archive' else [],
        'active_count': active_plans.count(),
        'archive_count': archive_plans.count(),
        'today': today,
    }
    return render(request, 'training/partials/plans_tab_content.html', context)


@login_required
@require_POST
def clear_active_htmx(request):
    """HTMX очистка активных планов"""
    active_plans = WorkoutPlan.objects.filter(user=request.user, is_active=True)
    active_plans.delete()
    return redirect('plans_list_partial')


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
    return redirect('plans_list_partial')

@login_required
@require_POST
def delete_plan_htmx(request, pk):
    """HTMX удаление плана без перезагрузки"""
    plan = get_object_or_404(WorkoutPlan, pk=pk, user=request.user)
    plan.delete()
    return HttpResponse("")