from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.template.response import TemplateResponse
from django.db.models import Q
from .models import Exercise, MuscleGroup, Equipment


class ExerciseListView(ListView):
    """Список упражнений с фильтрацией"""
    model = Exercise
    template_name = 'exercises/exercise_list.html'
    context_object_name = 'exercises'
    paginate_by = 12

    FILTER_MAPPING = {
        'exercise_type': lambda qs, val: qs.filter(exercise_type=val),
        'difficulty': lambda qs, val: qs.filter(difficulty=val),
        'muscle': lambda qs, val: qs.filter(muscle_groups__slug=val),
        'equipment': lambda qs, val: qs.filter(equipment__slug=val),
    }

    def get_queryset(self):
        queryset = Exercise.objects.filter(is_active=True)

        # Поиск
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )

        # Фильтры
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                queryset = filter_func(queryset, value)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['muscle_groups'] = MuscleGroup.objects.filter(is_group=True)
        context['equipment'] = Equipment.objects.all()
        context['exercise_types'] = Exercise.TYPE_CHOICES
        context['difficulties'] = Exercise.DIFFICULTY_CHOICES

        # Сохраняем параметры фильтрации
        context['filter_params'] = {
            'q': self.request.GET.get('q', ''),
            'exercise_type': self.request.GET.get('exercise_type', ''),
            'difficulty': self.request.GET.get('difficulty', ''),
            'muscle': self.request.GET.get('muscle', ''),
            'equipment': self.request.GET.get('equipment', ''),
        }
        return context

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        # HTMX поддержка
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'exercises/exercise_grid.html', context)

        return TemplateResponse(request, self.template_name, context)


class ExerciseDetailView(DetailView):
    """Детальная страница упражнения"""
    model = Exercise
    template_name = 'exercises/exercise_detail.html'
    slug_field = 'slug'
    context_object_name = 'exercise'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise = self.get_object()

        # Похожие упражнения
        context['similar_exercises'] = Exercise.objects.filter(
            primary_muscles__in=exercise.primary_muscles.all()
        ).exclude(id=exercise.id).filter(is_active=True).distinct()[:4]

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()

        # HTMX поддержка
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'exercises/exercise_detail_content.html', context)

        return TemplateResponse(request, self.template_name, context)


class ExerciseSearchView(TemplateView):
    """Быстрый поиск упражнений (для HTMX)"""
    template_name = 'exercises/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')

        if query:
            context['exercises'] = Exercise.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            ).filter(is_active=True)[:5]
        else:
            context['exercises'] = []

        context['query'] = query
        return context