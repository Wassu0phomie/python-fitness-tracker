import requests
import json
from django.shortcuts import render


# ... ваши остальные импорты ...

def recipe_list(request):
    query = request.GET.get('q', 'healthy')
    api_key = 'f1824f216dd542488cc1c392fc36d60d'  # Сюда вставьте ключ от Spoonacular
    url = f'https://api.spoonacular.com/recipes/complexSearch?query={query}&number=12&apiKey={api_key}'

    try:
        response = requests.get(url)
        data = response.json()
        recipes = data.get('results', [])
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")
        recipes = []

    return render(request, 'main/recipe_list.html', {
        'recipes': recipes,
        'query': query
    })