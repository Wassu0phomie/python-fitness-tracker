from django.views.generic import TemplateView
from training.models import WorkoutPlan
# from progress.models import ProgressPhoto
from datetime import date
from django.shortcuts import render
from django.utils import timezone

def welcome(request):
    return render(request, 'welcome.html')


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            # 1. Фильтруем только реально активные планы
            # План активен, если флаг is_active=True И дата окончания еще не прошла
            today = timezone.now().date()
            context['active_plans'] = WorkoutPlan.objects.filter(
                user=user,
                is_active=True,
                end_date__gte=today  # Дата окончания больше или равна сегодняшней
            ).order_by('-start_date')

            # 2. Получение профиля
            # В Django лучше использовать hasattr, чтобы не ловить ошибки через try/except
            if hasattr(user, 'profile'):
                context['profile'] = user.profile
            else:
                context['profile'] = None

            # 3. Передаем дату (объект timezone.now() для фильтра |date в шаблоне)
            context['date'] = timezone.now()

            # 4. Фото прогресса (заглушка)
            context['recent_photos'] = [] # Пока модель не готова, передаем пустой список

        return context
