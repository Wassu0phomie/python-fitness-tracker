from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.html import strip_tags
from django.core.validators import RegexValidator

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации нового атлета в FITAPP"""

    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
            'placeholder': 'EMAIL'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
            'placeholder': 'FIRST NAME'
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
            'placeholder': 'LAST NAME'
        })
    )

    class Meta:
        model = User
        # Пароли password1 и password2 уже встроены в UserCreationForm
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже используется.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = None  # Гарантируем отсутствие username
        if commit:
            user.save()
        return user


class CustomUserLoginForm(AuthenticationForm):
    """Форма входа (Email вместо Username)"""

    username = forms.CharField(
        label="Email",
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
            'placeholder': 'EMAIL'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
            'placeholder': 'PASSWORD'
        })
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Неверный email или пароль.')
            elif not self.user_cache.is_active:
                raise forms.ValidationError('Этот аккаунт деактивирован.')
        return self.cleaned_data


class CustomUserUpdateForm(forms.ModelForm):
    """Форма редактирования профиля атлета"""

    phone = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', "Введите корректный номер телефона.")],
        widget=forms.TextInput(attrs={
            'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
            'placeholder': 'PHONE NUMBER'
        })
    )

    class Meta:
        model = User
        # Убедись, что эти поля есть в твоей модели CustomUser в models.py
        fields = ('first_name', 'last_name', 'email', 'phone', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                'placeholder': 'FIRST NAME'}),
            'last_name': forms.TextInput(attrs={
                'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                'placeholder': 'LAST NAME'}),
            'email': forms.EmailInput(attrs={
                'class': 'dotted-input w-full py-3 text-sm font-medium text-gray-900 placeholder-gray-500',
                'placeholder': 'EMAIL'}),
            # Кастомизируем поле выбора файла
            'avatar': forms.FileInput(attrs={
                'class': 'form-control form-control-sm mt-1',
                'accept': 'image/*'  # Чтобы предлагал только картинки
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Этот email уже занят другим пользователем.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        # Очистка всех строковых полей от HTML-тегов для безопасности
        for field in cleaned_data:
            if isinstance(cleaned_data[field], str):
                cleaned_data[field] = strip_tags(cleaned_data[field])
        return cleaned_data

from .models import UserProgress

class UserProgressUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProgress
        fields = ('weight', 'height')
        widgets = {
            'weight': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.1'}),
            'height': forms.NumberInput(attrs={'class': 'form-control-custom', 'step': '0.1'}),
        }