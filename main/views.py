from django.views.generic import TemplateView
# from training.models import WorkoutPlan
# from progress.models import ProgressPhoto
from datetime import date
from django.shortcuts import render

def welcome(request):
    return render(request, 'welcome.html')

class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
