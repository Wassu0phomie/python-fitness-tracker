from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserUpdateForm, UserProgressUpdateForm
from django.utils import timezone
from training.models import WorkoutPlan



def welcome(request):
    return render(request, 'welcome.html')

# ========== ПРОФИЛЬ И РЕДАКТИРОВАНИЕ ==========

@login_required
def profile_view(request):
    user = request.user
    today = timezone.now().date()

    # Берем логику из старого IndexView
    active_plans = WorkoutPlan.objects.filter(
        user=user,
        is_active=True,
        end_date__gte=today
    ).order_by('-start_date')

    # Получаем последние замеры (модель UserProgress из ваших models.py)
    # Используем related_name='progress_logs'
    latest_progress = user.progress_logs.first()

    context = {
        'user': user,
        'active_plans': active_plans,
        'profile': latest_progress,
        'date': timezone.now(),
        'recent_photos': [],  # Заглушка
    }

    # Путь к шаблону уже в папке users
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