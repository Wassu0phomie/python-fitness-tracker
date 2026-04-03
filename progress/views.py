import json
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count
from .models import WorkoutLog, ProgressEntry
from collections import defaultdict
@login_required
def progress_view(request):
    # --- Инициализация дат ---
    today_local = timezone.localtime(timezone.now()).date()
    end_date = today_local
    start_date = end_date - timedelta(days=364)
    start_date_month = today_local - timedelta(days=30)

    # --- 1. Muscle Split (Круговая диаграмма) за 30 дней ---
    muscle_stats = (WorkoutLog.objects.filter(
        user=request.user,
        completed_at__date__gte=start_date_month
    )
    .filter(workout_day__exercises__exercise__muscle_groups__is_group=True)  # Фильтр по группам
    .values('workout_day__exercises__exercise__muscle_groups__name')
    .annotate(count=Count('workout_day__exercises__exercise__muscle_groups'))
    .order_by('-count'))

    # Обновите ключи в генераторах списков
    muscle_labels = [s['workout_day__exercises__exercise__muscle_groups__name'] for s in muscle_stats if
                     s['workout_day__exercises__exercise__muscle_groups__name']]
    muscle_data = [s['count'] for s in muscle_stats if s['workout_day__exercises__exercise__muscle_groups__name']]

    # --- 2. Активность за месяц (Линейный график) ---
    activity_stats = (WorkoutLog.objects.filter(
        user=request.user,
        completed_at__date__gte=start_date_month
    )
    .values('completed_at__date')
    .annotate(count=Count('id'))
    .order_by('completed_at__date'))

    activity_labels = [s['completed_at__date'].strftime('%d.%m') for s in activity_stats]
    activity_data = [s['count'] for s in activity_stats]

    # --- 3. Календарь (Heatmap) - СНАЧАЛА СОБИРАЕМ ДАННЫЕ ---
    year_stats = WorkoutLog.objects.filter(
        user=request.user,
        completed_at__date__range=[start_date, end_date]
    ).values('completed_at__date').annotate(count=Count('id'))

    # Словарь для быстрого доступа к количеству тренировок по дате
    stats_dict = {s['completed_at__date']: s['count'] for s in year_stats}

    heatmap_data = []
    months_labels = []
    last_month = -1
    curr = start_date

    # Теперь запускаем цикл, когда stats_dict уже существует
    while curr <= end_date:
        count = stats_dict.get(curr, 0)
        level = min(count, 4) if count > 0 else 0

        # Сбор подписей месяцев
        if curr.month != last_month:
            months_labels.append({
                'name': curr.strftime('%b'),
                'column': (curr - start_date).days // 7
            })
            last_month = curr.month

        heatmap_data.append({'date': curr, 'level': level, 'count': count})
        curr += timedelta(days=1)

    # --- 4. Фотографии (Группировка) ---
    raw_photos = ProgressEntry.objects.filter(user=request.user).order_by('-created_at')

    grouped_photos = defaultdict(list)
    for photo in raw_photos:
        # Ключ: "Март 2026"
        month_key = photo.created_at.strftime('%B %Y')
        grouped_photos[month_key].append(photo)

    return render(request, 'progress/progress_list.html', {
        'heatmap_data': heatmap_data,
        'months_labels': months_labels,
        'grouped_photos': dict(grouped_photos),  # Передаем сгруппированный словарь
        'total_workouts': sum(stats_dict.values()),
        'muscle_labels_json': json.dumps(muscle_labels, ensure_ascii=False),
        'muscle_data_json': json.dumps(muscle_data),
        'labels_json': json.dumps(activity_labels),
        'data_json': json.dumps(activity_data),
    })
@login_required
def upload_progress_htmx(request):
    if request.method == 'POST':
        entry = ProgressEntry.objects.create(
            user=request.user,
            image=request.FILES.get('image'),
            weight=request.POST.get('weight'),
            comment=request.POST.get('comment')
        )
        return render(request, 'progress/partials/photo_card.html', {'photo': entry})

@login_required
def delete_photo_htmx(request, photo_id):
    photo = get_object_or_404(ProgressEntry, id=photo_id, user=request.user)
    photo.delete()
    return HttpResponse("")