import locale
import re
from datetime import datetime, timedelta, time
from django.db.models import Q

from dateutil.parser import parse
from django.utils import timezone
from django.utils.html import escape

from .qdrant import search_files_in_group
from ..models import Reminder, UploadedFile, GroupMember, Group, Task, Event

locale.setlocale(locale.LC_TIME, "pl_PL.UTF-8")

from openai import OpenAI
from decouple import config

OPENAI_API_KEY = config("OPENAI_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENAI_API_KEY,
)


def generate_response(prompt):
    completion = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content


AVAILABLE_FUNCTIONS = [
    "Pokazywanie zadań",
    "Pokazywanie wydarzeń",
    "Ustawianie przypomnień",
    "Tworzenie wydarzeń",
    "Wyszukiwanie plików"
]

def identify_function(command):
    prompt = (
        "Na podstawie polecenia użytkownika określ funkcję. "
        f"Dostępne funkcje: {', '.join(AVAILABLE_FUNCTIONS)}. "
        "Zwróć dokładną nazwę funkcji lub 'nieznana funkcja'.\n\n"
        f"Polecenie: '{command}'"
    )
    return generate_response(prompt)

def parse_date_with_keywords(date_input):
    date_input = date_input.strip().lower()
    now = datetime.now()

    dni_tygodnia = {
        "poniedzialek": 0, "wtorek": 1, "sroda": 2, "czwartek": 3,
        "piatek": 4, "sobota": 5, "niedziela": 6
    }

    if date_input.startswith("w "):
        parts = date_input[2:].split(" o ")
        dzien = parts[0].strip()
        godzina = int(parts[1]) if len(parts) > 1 else None

        if dzien in dni_tygodnia:
            days_difference = (dni_tygodnia[dzien] - now.weekday()) % 7 or 7
            target_date = now + timedelta(days=days_difference)
            return target_date.replace(hour=godzina or 12, minute=0, second=0) if godzina is not None else target_date

    mapping = {
        "dzis": now, "dzisiaj": now,
        "jutro": now + timedelta(days=1),
        "za tydzien": now + timedelta(weeks=1),
        "za rok": now.replace(year=now.year + 1),
    }

    # Obsługa standardowych słów kluczowych
    if date_input in ["dzis", "dzisiaj"]:
        return now
    elif date_input == "jutro":
        return now + timedelta(days=1)
    elif date_input == "za tydzien":
        return now + timedelta(weeks=1)
    elif date_input == "za miesiac":
        # Przejście do kolejnego miesiąca
        next_month = now.month + 1 if now.month < 12 else 1
        year_increment = 1 if now.month == 12 else 0
        return now.replace(year=now.year + year_increment, month=next_month)
    elif date_input == "za rok":
        return now.replace(year=now.year + 1)
    elif date_input.startswith("o "):  # Np. "o 18"
        try:
            hour = int(date_input.split()[1])
            return now.replace(hour=hour, minute=0, second=0, microsecond=0)
        except ValueError:
            raise ValueError("Niepoprawny format godziny.")

    try:
        return parse(date_input, dayfirst=True)  # Obsługuje daty "22.01.2025", "2025-01-22 18:00", itp.
    except Exception as e:
        raise ValueError(f"Nie udało się zinterpretować daty: {str(e)}")


def show_tasks(user, status=None, overdue=False, due_today=False):
    filters = {"assignee": user}
    if status:
        filters["status"] = status
    if overdue:
        filters["is_overdue"] = True
    if due_today:
        filters["due_date"] = timezone.now().date()

    tasks = Task.objects.filter(**filters)

    if not tasks.exists():
        return "Nie masz żadnych zadań."

    return "Twoje zadania:\n" + "\n".join(
        f"{task.title} (Due: {task.due_date}, Status: {task.status}, Priority: {task.priority})"
        for task in tasks
    )

def show_events(user, upcoming=False, past=False, event_type=None, due_today=False):
    user_groups = GroupMember.objects.filter(user=user).values_list('group', flat=True)

    filters = Q(group__in=user_groups)
    if upcoming:
        filters &= Q(start_date__gte=timezone.now())
    if past:
        filters &= Q(start_date__lt=timezone.now())
    if event_type:
        filters &= Q(type=event_type)
    if due_today:
        filters &= Q(start_date__date=timezone.now().date())

    events = Event.objects.filter(filters)

    if not events.exists():
        return "Nie masz żadnych wydarzeń."

    return "Twoje wydarzenia:\n" + "\n".join(
        f"{event.name} ({event.start_date} - {event.end_date})" for event in events
    )

def create_reminder(remind_at, reminder_message, user):
    """Funkcja pomocnicza do tworzenia przypomnienia w bazie danych"""
    reminder = Reminder.objects.create(
        title="Reminder",
        content=reminder_message,
        time=remind_at,
        user=user
    )

    return f"Ustawiono przypomnienie na {parse(remind_at, dayfirst=True).strftime('%d-%m-%Y %H:%M')}: '{reminder_message}'."


def set_reminder(user_input, request):
    step = request.session.get('reminder_creation_step', '')
    reminder_data = request.session.get('reminder_data', {})
    if step == "ask_title":
        reminder_data['name'] = user_input
        request.session['reminder_data'] = reminder_data
        request.session['reminder_creation_step'] = "ask_date"
        return "Podaj date przypomnienia:"
    if step == "ask_date":
        try:
            start_date = parse_date_with_keywords(user_input)
            today = timezone.now()
            if start_date.date() < today.date():
                return f"Niepoprawna data. data nie moze być wcześniej niz dzisiaj"
            date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            print(start_date)
            reminder_data['date'] = date_str
            request.session['reminder_data'] = reminder_data
            reminder = create_reminder(reminder_data['date'], reminder_data['name'], request.user)
            clear(request)
            return reminder
        except ValueError as e:
            return f"Niepoprawny format daty. Spróbuj ponownie. Szczegóły: {escape(str(e))}"
    if step == "":
        request.session['reminder_creation_step'] = "ask_title"
        return "Podaj tytuł przypomnienia"


def chatbot_search(user_message, user, offset=0):
    match = re.match(r'wyszukaj pliki zawierajace (.*)( w grupie (\d+))?', user_message)
    if match:
        groups = Group.objects.filter(id__in=GroupMember.objects.filter(user=user).values('group'))
        query_sentence = match.group(1)
        group_id = int(match.group(3) or 0)
        if group_id == 0:
            files = UploadedFile.objects.filter(group__in=groups)
        else:
            files = UploadedFile.objects.filter(group_id=group_id)
        ids = [file.qdrant_id for file in files]
        qdrant_results = search_files_in_group(query_sentence, ids, limit=5, offset=offset)
        result_files = []
        for result in qdrant_results:
            try:
                file = files.get(qdrant_id=result.id)
                group_id = file.group.id
                match_percentage = result.score * 100
                result_files.append({
                    'title': file.name,
                    'match_percentage': round(match_percentage, 2),
                    'group_id': group_id
                })
            except UploadedFile.DoesNotExist:
                continue
        if result_files:
            response = f"Znaleziono {len(result_files)} pliki:"
            for file in result_files:
                response += f"<p> Tytuł: {file['title']}, Dopasowanie: {file['match_percentage']}%, Grupa ID: {file['group_id']}</p>"
        else:
            response = "Nie znaleziono plików, które pasują do zapytania."

    else:
        response = "Nie rozumiem komendy. Użyj formatu: 'Wyszukaj pliki zawierające \"<zdanie>\"' lub 'Wyszukaj pliki zawierające \"<zdanie>\" w grupie {group_id}'."
        print("not match")

    return response


def get_event_type(name, description):
    """Automatyczne określenie typu na podstawie nazwy lub opisu."""
    meeting_keywords = ["spotkanie", "konferencja", "meeting", "narada"]
    text = f"{name} {description}".lower()
    if any(word in text for word in meeting_keywords):
        return "spotkanie"
    return "wydarzenie"


def clear(request):
    request.session.pop('event_creation_step', None)
    request.session.pop('event_data', None)
    request.session.pop('reminder_creation_step', None)
    request.session.pop('reminder_data', None)


def event_creator_with_step(user_input, request):
    steps = ["is_group", 'ask_group', 'ask_title' 'is_all_day', 'ask_date', 'ask_start_date', 'ask_end_date',
             'ask_description']
    step = request.session.get('event_creation_step', '')
    event_data = request.session.get('event_data', {})
    if step == "is_group":
        if user_input == "tak":
            request.session['event_creation_step'] = "ask_group"
            return "Do której grupy należy to wydarzenie? Podaj nazwę lub id grupy:"
        elif user_input == "nie":
            request.session['event_creation_step'] = "is_all_day"
            return "Czy wydarzenie trwa cały dzień?:"
        else:
            return "Napisz Tak lub Nie"
    if step == "ask_group":
        try:
            if user_input.isdigit():
                group = Group.objects.get(id=user_input)
            else:
                group = Group.objects.get(stylized_name=user_input)

            if not GroupMember.objects.filter(group=group, user=request.user).exists():
                return "Nie należysz do tej grupy. Podaj poprawną grupę:"

            event_data['group'] = group.id
            request.session['event_data'] = event_data
            request.session['event_creation_step'] = "ask_title"
            return "Podaj nazwę wydarzenia:"

        except Group.DoesNotExist:
            return "Nie znaleziono takiej grupy. Podaj poprawną nazwę lub id grupy:"
        except Exception as e:
            return f"Wystąpił błąd: {str(e)}"

    if step == "ask_title":
        event_data['name'] = user_input
        request.session['event_data'] = event_data
        request.session['event_creation_step'] = "is_all_day"
        return "Czy wydarzenie jest cały dzień?:"

    if step == "is_all_day":
        if user_input == "tak":
            request.session['event_creation_step'] = "ask_date"
            event_data['is_all_day'] = False
            request.session['event_data'] = event_data
            return "Podaj datę wydarzenia:"
        elif user_input == "nie":
            event_data['is_all_day'] = True
            request.session['event_data'] = event_data
            request.session['event_creation_step'] = "ask_start_date"
            return "Podaj datę rozpoczęcia wydarzenia:"
        else:
            return "Napisz Tak lub Nie"

    if step == "ask_date":
        try:
            start_date = parse_date_with_keywords(user_input)
            date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            event_data['start_date'] = date_str
            request.session['event_data'] = event_data
            request.session['event_creation_step'] = "ask_description"
            return "Podaj opis"
        except ValueError as e:
            return f"Niepoprawny format daty. Spróbuj ponownie. Szczegóły: {escape(str(e))}"

    if step == "ask_start_date":
        try:
            start_date = parse_date_with_keywords(user_input)
            end_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            event_data['start_date'] = end_date_str
            request.session['event_data'] = event_data
            request.session['event_creation_step'] = "ask_end_date"
            return "Podaj datę zakończenia wydarzenia:"
        except ValueError as e:
            return f"Niepoprawny format daty. Spróbuj ponownie. Szczegóły: {escape(str(e))}"

    elif step == "ask_end_date":
        try:
            end_date = parse_date_with_keywords(user_input)
            end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
            event_data['end_date'] = end_date_str
            request.session['event_data'] = event_data
            request.session['event_creation_step'] = "ask_description"
            return "Podaj opis wydarzenia:"
        except ValueError as e:
            return f"Niepoprawny format daty. Spróbuj ponownie. Szczegóły: {escape(str(e))}"

    elif step == "ask_description":
        request.session['event_data'] = event_data
        event_type = get_event_type(event_data['name'], user_input)
        start_date = datetime.strptime(event_data['start_date'], '%Y-%m-%d %H:%M:%S')
        if event_data['is_all_day']:
            end_date = datetime.strptime(event_data['end_date'], '%Y-%m-%d %H:%M:%S')
        else:
            end_date = datetime.combine(start_date.date(), time(23, 59, 59))
        new_event = Event.objects.create(
            group=Group.objects.get(id=event_data['group']),
            name=event_data['name'],
            description=user_input,
            start_date=start_date,
            end_date=end_date,
            type=event_type,
            created_by=request.user,
            is_all_day=event_data['is_all_day'],
        )

        request.session.pop('event_creation_step', None)
        request.session.pop('event_data', None)
        event_start = new_event.start_date.strftime('%d.%m.%y')  # Format: dzień.miesiąc.rok
        event_end = new_event.end_date.strftime('%d.%m.%y')  # Format: dzień.miesiąc.rok

        message = (f"Wydarzenie '{escape(new_event.name)}' zostało utworzone! "
                   f"Typ: {new_event.get_type_display()}, Grupa: {new_event.group.name}, "
                   f"Rozpoczyna się: {event_start}, kończy: {event_end}.")
        return message
    else:
        request.session.pop('event_creation_step', None)
        request.session.pop('event_data', None)
        return None


def analyze_event_category(user_input, user):
    prompt = f"""
    Użytkownik wpisał: "{user_input}".
    Określ, czy użytkownik chce zobaczyć wydarzenia:
    - "na dziś"
    - "przeszłe"
    - "nadchodzące"

    Zwróć jedynie jedno słowo: "dzisiaj", "przeszłe" lub "nadchodzące".
    """
    category = generate_response(prompt)
    if category == "nadchodzące":
        show_events(user, upcoming=True)
    elif category == "przeszłe":
        show_events(user, past=True)
    elif category == "dzisiaj":
        show_events(user, due_today=True)
    else:
        print("Nie rozpoznano kategorii wydarzeń. Spróbuj ponownie.")


def get_chatbot_response(user_input, request):
    # last_msg = request.session.get('last_msg', '')
    # request.session['last_msg'] = user_input
    if user_input == "!clear":
        clear(request)
        return
    if user_input == "stop":
        clear(request)
        return "stop"
    if user_input.lower() == "!help":
        clear(request)
        return get_help()
    if request.session.get('event_creation_step', ''):
        return event_creator_with_step(user_input, request)
    if request.session.get('reminder_creation_step', ''):
        return set_reminder(user_input, request)
    responses = {
        r"czesc": "Cześć! Jak mogę Ci pomóc?",
        r"co to jest django\?": "Django to framework webowy w Pythonie.",
        r"do widzenia": "Do widzenia! Miłego dnia!",
    }
    for pattern, response in responses.items():
        if re.match(pattern, user_input, re.IGNORECASE):
            clear(request)
            return response
    # get_command(user_input, request)
    response = identify_function(user_input)
    print(response)
    if "Pokazywanie zadań" in response:
        return show_tasks(request.user)
    elif "Pokazywanie wydarzeń" in response:
        return analyze_event_category(user_input, request.user)
    elif "Tworzenie wydarzeń" in response:
        request.session['event_creation_step'] = "is_group"
        return "Czy wydarzenie dla całej grupy? <br>Napisz Tak lub Nie"
    elif "Ustawianie przypomnień" in response:
        return set_reminder(user_input, request)
    elif "Wyszukiwanie plików" in response:
        return chatbot_search(user_input, request.user)
    else:
        return "Przepraszam, nie rozumiem tego polecenia."


def get_help():
    help_message = """
Dostępne komendy:

1. **ustaw przypomnienie za X minut/godzin/dni: [wiadomość]**  
   Ustaw przypomnienie po określonym czasie.  
   Przykład: `ustaw przypomnienie za 10 minut: Zadzwoń do klienta`

2. **ustaw przypomnienie na DD.MM.YYYY o godzinie HH:MM: [wiadomość]**  
   Ustaw przypomnienie na konkretną datę i godzinę.  
   Przykład: `ustaw przypomnienie na 10.01.2025 o godzinie 14:30: Spotkanie z klientem`

3. **przypomnij za X minut/godzin/dni: [wiadomość]**  
   Alternatywna wersja komendy do ustawiania przypomnienia.  
   Przykład: `przypomnij za 1 godzinę: Zadzwoń do klienta`

4. **przypomnij na DD.MM.YYYY o godzinie HH:MM: [wiadomość]**  
   Alternatywna wersja komendy do ustawiania przypomnienia na konkretną datę i godzinę.  
   Przykład: `przypomnij na 15.02.2025 o godzinie 09:00: Spotkanie z zespołem`

5. **co to jest django?**  
   Wyświetla informację o frameworku Django.

6. **witaj**  
   Przywitanie z botem.

7. **do widzenia**  
   Pożegnanie z botem.

8. **!help**  
   Wyświetla listę dostępnych komend.
"""
    return help_message.strip()
