from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.middleware.csrf import get_token  # Importuj funkcję CSRF
from .site_bot import get_bot_response  # Funkcja generująca odpowiedź bota
import json

def homepage(request):
    context = {'csrf_token': get_token(request)}  # Dodaj token CSRF do kontekstu
    return render(request, 'myapp/home.html', context)

def get_calendar_widget(request):
    return render(request, 'myapp/calendar-widget.html')

def tasks(request):
    return render(request, 'myapp/Tasks.html')

def singleTask(request):
    return render(request, 'myapp/singleTask.html')

def calendar(request):
    return render(request, 'myapp/calendar.html')

def calendar_month(request):
    return render(request, 'myapp/months.html')

def calendar_week(request):
    return render(request, 'myapp/week.html')

def calendar_day(request):
    return render(request, 'myapp/day.html')

def teams(request):
    return render(request, 'myapp/groups.html')

def teamPage(request):
    return render(request, 'myapp/teamPage.html')

def projects(request):
    return render(request, 'myapp/projects.html')

def projects_board(request):
   return render(request, 'myapp/projects-board.html')

def project(request):
    return render(request, 'myapp/project.html')

def task(request):
    return render(request, 'myapp/task.html')

def posts_content(request):
    return render(request, 'myapp/feed.html')

def files_content(request):
    return render(request, 'myapp/files.html')

def task_list(request):
    return render(request, 'myapp/taskList.html')

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


def load_reminder_content(request, view_type):
    # Wybór odpowiedniego szablonu
    if view_type == 'today':
        template = 'myapp/reminder-widget-today.html'
    elif view_type == 'tomorrow':
        template = 'myapp/reminder-widget-tommorow.html'
    elif view_type == 'week':
        template = 'myapp/reminder-widget-week.html'
    elif view_type == 'all':
        template = 'myapp/reminder-widget-all.html'
    else:
        template = 'myapp/reminder-widget-today.html'  # domyślny

    # Renderowanie szablonu
    html_content = render(request, template)
    
    return JsonResponse({'html': html_content.content.decode()})

def load_task_content(request, view_type):
    # Wybór odpowiedniego szablonu na podstawie view_type
    if view_type == 'to-do':
        template = 'myapp/taskToDoWidget.html'
    elif view_type == 'in-progress':
        template = 'myapp/taskInProgressWidget.html'
    elif view_type == 'overdue':
        template = 'myapp/taskOverdueWidget.html'
    elif view_type == 'completed':
        template = 'myapp/taskCompletedWidget.html'
    else:
        template = 'myapp/taskToDoWidget.html'  # domyślny

    # Renderowanie szablonu i zwrócenie go jako JSON
    html_content = render(request, template)
    
    return JsonResponse({'html': html_content.content.decode()})
    