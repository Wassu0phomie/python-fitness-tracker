from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator

from .models import CustomUser, UserProgress
from .forms import CustomUserCreationForm, CustomUserUpdateForm, UserProgressUpdateForm
from django.utils import timezone
from training.models import WorkoutPlan
from progress.models import WorkoutLog, ProgressEntry

def welcome(request):
    return render(request, 'welcome.html')

# ========== ПРОФИЛЬ И РЕДАКТИРОВАНИЕ ==========

@login_required
def profile_view(request):
    user = request.user
    today = timezone.now().date()

    # Проверка первого визита
    is_first_visit = request.session.get('is_first_visit', True)
    show_welcome_tour = False

    # 1. Считаем реальные тренировки из лога
    total_workouts = WorkoutLog.objects.filter(user=user).count()

    # 2. Логика опыта (1 тренировка = 100 XP)
    xp_for_next_level = 1000
    total_xp = total_workouts * 100
    user_level = (total_xp // xp_for_next_level) + 1
    xp_progress = total_xp % xp_for_next_level
    xp_percentage = (xp_progress / xp_for_next_level) * 100

    # 3. Спортивные ранги
    if total_workouts < 5:
        current_rank = "Новичок"
    elif total_workouts < 15:
        current_rank = "Любитель"
    elif total_workouts < 35:
        current_rank = "Атлет"
    elif total_workouts < 70:
        current_rank = "Профи"
    else:
        current_rank = "Мастер"

    # 4. Получаем данные профиля и фото
    active_plans = WorkoutPlan.objects.filter(user=user, is_active=True, end_date__gte=today)
    latest_progress = user.progress_logs.first()
    recent_photos = ProgressEntry.objects.filter(user=user).exclude(image='').order_by('-created_at')[:3]

    context = {
        'user': user,
        'active_plans': active_plans,
        'profile': latest_progress,
        'total_workouts': total_workouts,
        'user_level': user_level,
        'current_rank': current_rank,
        'xp_progress': xp_progress,
        'xp_percentage': xp_percentage,
        'xp_for_next_level': xp_for_next_level,
        'recent_photos': recent_photos,
        'today': timezone.now(),
        'show_welcome_tour': show_welcome_tour,
    }
    return render(request, 'users/profile.html', context)


@login_required
def delete_profile(request):
    """Удаление аккаунта пользователя"""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Ваш аккаунт был безвозвратно удален. Нам жаль, что вы уходите.")
        return redirect('welcome')

    return redirect('profile')


@login_required
def edit_profile_view(request):
    user = request.user
    # Получаем последнюю запись прогресса или создаем новую, если записей нет
    progress = user.progress_logs.first() or UserProgress(user=user)

    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        progress_form = UserProgressUpdateForm(request.POST, instance=progress)

        if user_form.is_valid() and progress_form.is_valid():
            user_form.save()
            # При сохранении прогресса убеждаемся, что связь с юзером установлена
            new_progress = progress_form.save(commit=False)
            new_progress.user = user
            new_progress.save()

            messages.success(request, "Профиль и параметры тела обновлены!")
            return redirect('profile')
    else:
        user_form = CustomUserUpdateForm(instance=user)
        progress_form = UserProgressUpdateForm(instance=progress)

    return render(request, 'users/edit_profile.html', {
        'form': user_form,
        'progress_form': progress_form
    })

# ========== РЕГИСТРАЦИЯ И АКТИВАЦИЯ ==========

def register(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Для разработки активация сразу, в продакшене лучше через email
            user.save()
            messages.success(request, "Регистрация прошла успешно! Теперь вы можете войти.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def activate(request, uidb64, token):
    """Активация аккаунта через Email"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Ваш аккаунт успешно активирован!")
        return redirect('profile')
    else:
        messages.error(request, "Ссылка активации недействительна.")
        return redirect('welcome')