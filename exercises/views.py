from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.template.response import TemplateResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from .models import Exercise, MuscleGroup, Equipment


class ExerciseListView(ListView):
    """Список упражнений с фильтрацией"""
    model = Exercise
    template_name = 'exercises/exercise_list.html'
    context_object_name = 'exercises'
    paginate_by = 12

    def get_queryset(self):
        queryset = Exercise.objects.filter(is_active=True)

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )

        exercise_type = self.request.GET.get('exercise_type')
        if exercise_type:
            queryset = queryset.filter(exercise_type=exercise_type)

        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        muscle = self.request.GET.get('muscle')
        if muscle:
            queryset = queryset.filter(muscle_groups__slug=muscle)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['muscle_groups'] = MuscleGroup.objects.filter(is_group=True)
        context['equipment'] = Equipment.objects.all()
        context['exercise_types'] = Exercise.TYPE_CHOICES
        context['difficulties'] = Exercise.DIFFICULTY_CHOICES

        context['filter_params'] = {
            'q': self.request.GET.get('q', ''),
            'exercise_type': self.request.GET.get('exercise_type', ''),
            'difficulty': self.request.GET.get('difficulty', ''),
            'muscle': self.request.GET.get('muscle', ''),
        }
        return context

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        if request.headers.get('HX-Request'):
            # Для HTMX запросов возвращаем только сетку
            page = request.GET.get('page', 1)
            paginator = Paginator(self.object_list, self.paginate_by)
            try:
                exercises = paginator.page(page)
            except EmptyPage:
                exercises = []

            context['exercises'] = exercises
            context['has_next'] = exercises.has_next() if exercises else False
            context['next_page'] = page + 1 if exercises.has_next() else None
            return render(request, 'exercises/partials/exercise_grid_items.html', context)

        return render(request, self.template_name, context)


class ExerciseDetailView(DetailView):
    """Детальная страница упражнения"""
    model = Exercise
    template_name = 'exercises/exercise_detail.html'
    slug_field = 'slug'
    context_object_name = 'exercise'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise = self.get_object()

        context['similar_exercises'] = Exercise.objects.filter(
            primary_muscles__in=exercise.primary_muscles.all()
        ).exclude(id=exercise.id).filter(is_active=True).distinct()[:4]

        return context

def htmx_load_more_exercises(request):
    """HTMX: Загрузка порций упражнений для бесконечного скролла"""
    queryset = Exercise.objects.filter(is_active=True)

    # Фильтрация (должна совпадать с основной вьюхой)
    q = request.GET.get('q')
    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(description__icontains=q))

    ex_type = request.GET.get('exercise_type')
    if ex_type:
        queryset = queryset.filter(exercise_type=ex_type)

    difficulty = request.GET.get('difficulty')
    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)

    muscle = request.GET.get('muscle')
    if muscle:
        queryset = queryset.filter(muscle_groups__slug=muscle)

    # Пагинация
    paginator = Paginator(queryset.distinct(), 12)
    page_number = int(request.GET.get('page', 1))

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        return render(request, 'exercises/partials/infinite_scroll_trigger.html', {'has_next': False})

    context = {
        'exercises': page_obj,
        'has_next': page_obj.has_next(),
        'next_page': page_number + 1,
        'filter_params': request.GET.dict(),
    }

    # Возвращаем только карточки и новый триггер
    return render(request, 'exercises/partials/exercise_grid_items.html', context)

