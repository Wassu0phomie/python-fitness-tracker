from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .forms import CustomUserCreationForm  # Убедись, что импорт формы верный

User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # 1. Создаем пользователя, но не активируем его
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # 2. Подготовка данных для письма
            current_site = get_current_site(request)
            mail_subject = 'Активация аккаунта FITAPP'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            # 3. Отправка письма
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])

            try:
                email.send()
                # Страница с уведомлением: "Проверьте почту"
                return render(request, 'registration/email_sent.html')
            except Exception as e:
                # Если почта не ушла (например, ошибка в .env или нет интернета)
                print(f"Ошибка отправки: {e}")
                return render(request, 'registration/register.html', {
                    'form': form,
                    'error': 'Ошибка при отправке письма. Проверьте настройки почты.'
                })
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def activate(request, uidb64, token):
    # ... твой существующий код функции activate (он верный) ...
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'registration/activation_success.html')
    else:
        return render(request, 'registration/activation_invalid.html')