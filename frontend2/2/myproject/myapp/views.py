from django.shortcuts import render
from django.http import JsonResponse
from django.middleware.csrf import get_token  # Importuj funkcję CSRF
from .site_bot import get_bot_response  # Funkcja generująca odpowiedź bota
import json

def homepage(request):
    context = {'csrf_token': get_token(request)}  # Dodaj token CSRF do kontekstu
    return render(request, 'myapp/home.html', context)

def tasks(request):
    return render(request, 'myapp/Tasks.html')

def calendar(request):
    return render(request, 'myapp/calendar.html')

def teams(request):
    return render(request, 'myapp/groups.html')

def teamPage(request):
    return render(request, 'myapp/teamPage.html')

def chat_with_bot(request):
    """
    Widok obsługujący zapytania do bota.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Przetwarzanie JSON z żądania
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "Message is required."}, status=400)

            # Wywołanie funkcji bota
            bot_response = get_bot_response(user_message)

            # Zwracanie odpowiedzi bota
            return JsonResponse({"response": bot_response})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=400)
