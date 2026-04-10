from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage


import requests
import json
from django.shortcuts import render



# ... ваши остальные импорты ...

def recipe_list(request):
    query = request.GET.get('q', 'healthy')
    api_key = 'f1824f216dd542488cc1c392fc36d60d'
    url = f'https://api.spoonacular.com/recipes/complexSearch?query={query}&number=12&apiKey={api_key}'

    try:
        response = requests.get(url)

        # Отладка - смотрим статус ответа
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:500]}")  # Первые 500 символов

        if response.status_code == 200:
            data = response.json()
            recipes = data.get('results', [])
        else:
            recipes = []
            # Показываем ошибку в консоли
            print(f"API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")
        recipes = []

    return render(request, 'main/recipe_list.html', {
        'recipes': recipes,
        'query': query
    })