import json
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count
from .models import WorkoutLog, ProgressEntry
from collections import defaultdict

# Словарь полных названий
MONTHS_RU_FULL = {
    'January': 'Январь', 'February': 'Февраль', 'March': 'Март', 'April': 'Апрель',
    'May': 'Май', 'June': 'Июнь', 'July': 'Июль', 'August': 'Август',
    'September': 'Сентябрь', 'October': 'Октябрь', 'November': 'Ноябрь', 'December': 'Декабрь'
}


@login_required
def progress_view(request):
    # --- Инициализация дат ---
    today_local = timezone.localtime(timezone.now()).date()
    end_date = today_local
    start_date = end_date - timedelta(days=364)
    start_date_month = today_local - timedelta(days=30)

    # --- 1. Muscle Split ---
    muscle_stats = (WorkoutLog.objects.filter(
        user=request.user,
        completed_at__date__gte=start_date_month
    )
                    .filter(workout_day__exercises__exercise__muscle_groups__is_group=True)
                    .values('workout_day__exercises__exercise__muscle_groups__name')
                    .annotate(count=Count('workout_day__exercises__exercise__muscle_groups'))
                    .order_by('-count'))

    muscle_labels = [s['workout_day__exercises__exercise__muscle_groups__name'] for s in muscle_stats]
    muscle_data = [s['count'] for s in muscle_stats]

    # --- 2. Активность за месяц ---
    activity_stats = (WorkoutLog.objects.filter(
        user=request.user,
        completed_at__date__gte=start_date_month
    )
                      .values('completed_at__date')
                      .annotate(count=Count('id'))
                      .order_by('completed_at__date'))

    activity_labels = [s['completed_at__date'].strftime('%d.%m') for s in activity_stats]
    activity_data = [s['count'] for s in activity_stats]

    # --- 3. Календарь (Heatmap) ---
    year_stats = WorkoutLog.objects.filter(
        user=request.user,
        completed_at__date__range=[start_date, end_date]
    ).values('completed_at__date').annotate(count=Count('id'))

    stats_dict = {s['completed_at__date']: s['count'] for s in year_stats}

    heatmap_data = []
    months_labels = []
    last_month = -1
    curr = start_date

    while curr <= end_date:
        count = stats_dict.get(curr, 0)
        level = min(count, 4) if count > 0 else 0

        # Сокращенные названия для календаря (Янв, Фев...)
        if curr.month != last_month:
            eng_month = curr.strftime('%B')
            rus_full = MONTHS_RU_FULL.get(eng_month, eng_month)
            # Берем первые 3 буквы. Для мая исключение, т.к. он короткий
            rus_short = rus_full[:3] if eng_month != 'May' else 'Май'

            months_labels.append({
                'name': rus_short,
                'column': (curr - start_date).days // 7
            })
            last_month = curr.month

        heatmap_data.append({'date': curr, 'level': level, 'count': count})
        curr += timedelta(days=1)

    # --- 4. Фотографии (Полные названия) ---
    raw_photos = ProgressEntry.objects.filter(user=request.user).order_by('-created_at')

    grouped_photos = defaultdict(list)
    for photo in raw_photos:
        eng_month = photo.created_at.strftime('%B')
        rus_month = MONTHS_RU_FULL.get(eng_month, eng_month)
        month_key = f"{rus_month} {photo.created_at.year}"
        grouped_photos[month_key].append(photo)

    return render(request, 'progress/progress_list.html', {
        'heatmap_data': heatmap_data,
        'months_labels': months_labels,
        'grouped_photos': dict(grouped_photos),
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