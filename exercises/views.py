from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.template.response import TemplateResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from .models import Exercise, MuscleGroup, Equipment


class ExerciseListView(TemplateView):
    """Список упражнений с фильтрацией"""
    template_name = 'exercises/exercise_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Базовый запрос
        queryset = Exercise.objects.filter(is_active=True)

        # Получаем параметры фильтрации из GET запроса
        q = self.request.GET.get('q', '')
        exercise_type = self.request.GET.get('exercise_type', '')
        difficulty = self.request.GET.get('difficulty', '')
        muscle = self.request.GET.get('muscle', '')

        # Применяем фильтры
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )

        if exercise_type:
            queryset = queryset.filter(exercise_type=exercise_type)

        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        if muscle:
            queryset = queryset.filter(muscle_groups__slug=muscle)

        # Пагинация
        paginator = Paginator(queryset.distinct(), 12)
        page_number = self.request.GET.get('page', 1)
        exercises = paginator.get_page(page_number)

        # Словарь с параметрами фильтрации для сохранения в форме
        filter_params = {
            'q': q,
            'exercise_type': exercise_type,
            'difficulty': difficulty,
            'muscle': muscle,
        }

        context.update({
            'exercises': exercises,
            'paginator': paginator,
            'muscle_groups': MuscleGroup.objects.filter(is_group=True),
            'equipment': Equipment.objects.all(),
            'exercise_types': Exercise.TYPE_CHOICES,
            'difficulties': Exercise.DIFFICULTY_CHOICES,
            'filter_params': filter_params,  # ← обязательно добавляем
        })

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # HTMX запрос → только сетка упражнений
        if request.headers.get('HX-Request'):
            return render(request, 'exercises/partials/exercise_grid.html', context)

        # Обычный запрос → полная страница
        return render(request, self.template_name, context)


class ExerciseDetailView(DetailView):
    """Детальная страница упражнения"""
    model = Exercise
    template_name = 'exercises/exercise_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise = self.get_object()

        context['similar_exercises'] = Exercise.objects.filter(
            primary_muscles__in=exercise.primary_muscles.all()
        ).exclude(id=exercise.id).filter(is_active=True).distinct()[:4]

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        if request.headers.get('HX-Request'):
            return render(request, 'exercises/exercise_detail.html', context)

        return render(request, self.template_name, context)