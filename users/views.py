from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserUpdateForm


# ========== ПРОФИЛЬ И РЕДАКТИРОВАНИЕ ==========

@login_required
def index(request):
    user = request.user

    if request.method == 'POST' and 'update_profile' in request.POST:
        # request.FILES нужен для обработки загруженного аватара
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлен!")
            return redirect('index')
    else:
        # Если это просто просмотр страницы (GET), создаем форму с данными юзера
        form = CustomUserUpdateForm(instance=user)

    # Убедитесь, что 'main/index.html' соответствует вашему расположению файла
    return render(request, 'main/index.html', {
        'user': user,
        'form': form,  # Передаем форму в шаблон под именем 'form'
    })


@login_required
def delete_profile(request):
    """Удаление аккаунта пользователя"""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Ваш аккаунт был безвозвратно удален. Нам жаль, что вы уходите.")
        return redirect('welcome')

    return redirect('index')


# ========== РЕГИСТРАЦИЯ И АКТИВАЦИЯ ==========

def register(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('index')

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
        return redirect('index')
    else:
        messages.error(request, "Ссылка активации недействительна.")
        return redirect('welcome')