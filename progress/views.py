import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import WorkoutLog, ProgressEntry
@login_required
def progress_view(request):
    # Данные для графика за последние 30 дней
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    stats = (WorkoutLog.objects.filter(user=request.user, completed_at__gte=thirty_days_ago)
             .annotate(date=TruncDate('completed_at'))
             .values('date')
             .annotate(count=Count('id'))
             .order_by('date'))

    labels = [s['date'].strftime('%d.%m') for s in stats]
    data = [s['count'] for s in stats]

    context = {
        'total_workouts': WorkoutLog.objects.filter(user=request.user).count(),
        'photos': ProgressEntry.objects.filter(user=request.user),
        'labels_json': json.dumps(labels),
        'data_json': json.dumps(data),
    }
    return render(request, 'progress/progress_list.html', context)
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import WorkoutLog, ProgressEntry
from datetime import timedelta


def progress_view(request):
    today_local = timezone.localtime(timezone.now()).date()

    end_date = today_local
    start_date = end_date - timedelta(days=364)

    # Получаем количество тренировок по дням
    stats = WorkoutLog.objects.filter(
        user=request.user,
        completed_at__date__range=[start_date, end_date]
    ).values('completed_at__date').annotate(count=Count('id'))

    # Создаем словарь для быстрого поиска: {date: count}
    stats_dict = {s['completed_at__date']: s['count'] for s in stats}
    photos = ProgressEntry.objects.filter(user=request.user).order_set('-created_at')
    # Генерируем полный список дней для сетки
    heatmap_data = []
    curr = start_date
    while curr <= end_date:
        count = stats_dict.get(curr, 0)
        # Определяем уровень интенсивности (от 0 до 4)
        level = min(count, 4) if count > 0 else 0
        heatmap_data.append({'date': curr, 'level': level, 'count': count})
        curr += timedelta(days=1)

    return render(request, 'progress/progress_list.html', {
        'heatmap_data': heatmap_data,
        'photos': photos
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
    return HttpResponse("") # HTMX удалит элемент из DOM
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
    return HttpResponse("") # HTMX удалит элемент из DOM