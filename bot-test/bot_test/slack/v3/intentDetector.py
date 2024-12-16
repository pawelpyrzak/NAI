import unicodedata
from transformers import pipeline
import re


def preprocess_text(text):
    text = text.lower()  # Zamiana na małe litery
    text = re.sub(r'[^\w\s]', '', text)
    return text


classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

INTENT_DESCRIPTIONS = {
    "todayTasks": [
        "tasks for today", "dzisiejsze zadania", "what needs to be done today",
        "what are my tasks today", "co mam do zrobienia dzisiaj", "zadania na dziś",
        "today's to-dos", "co muszę zrobić dzisiaj", "czy mam zadania na dziś"
    ],
    "upcomingTasks": [
        "upcoming tasks", "najbliższe zadania", "what's coming next", "tasks for the week",
        "zadania na tydzień", "weekly overview", "what tasks do I have this week",
        "kolejne zadania", "co będzie do zrobienia w przyszłości", "plan na przyszłość"
    ],
    "TodayMeetings": [
        "show today's meetings", "dzisiejsze spotkania", "spotkania na dziś",
        "what meetings do I have today", "dzisiejszy harmonogram spotkań", "czy mam spotkania dzisiaj",
        "list of today's meetings", "jakie spotkania mam dzisiaj", "plan spotkań na dzisiaj"
    ],
    "upcomingMeetings": [
        "upcoming meetings", "pokaż najbliższe spotkania", "najbliższe spotkania",
        "meetings for the next days", "spotkania na najbliższe dni", "meetings coming up",
        "co za spotkania będą w najbliższym czasie", "what meetings are coming up",
        "plan spotkań na przyszłość"
    ],
    "scheduleToday": [
        "show today's schedule", "kalendarz", "schedule", "dzisiejszy kalendarz",
        "co w kalendarzu", "plan na dziś", "harmonogram dnia", "what's on my calendar today",
        "jakie mam wydarzenia dzisiaj", "co mam dzisiaj w planie", "dzisiejszy plan dnia"
    ]
}


def remove_accents(input_str: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


def detect_intent(user_message: str, threshold: float) -> str:
    # Usuwanie polskich znaków z wiadomości użytkownika
    user_message_normalized = remove_accents(preprocess_text(user_message))

    # Sprawdzanie, czy wiadomość użytkownika zawiera któryś z opisów intencji
    for intent, descriptions in INTENT_DESCRIPTIONS.items():
        # Normalizowanie opisów intencji
        for desc in descriptions:
            if remove_accents(desc) in user_message_normalized:
                return intent

    # Łączenie wszystkich opisów w jedną listę i klasyfikowanie wiadomości użytkownika
    candidate_labels = [label for descriptions in INTENT_DESCRIPTIONS.values() for label in descriptions]
    result = classifier(user_message, candidate_labels, multi_label=False)

    # Dopasowanie najlepszego wyniku
    best_label, best_score = result["labels"][0], result["scores"][0]

    # Debugowanie
    print(f"Best label: {best_label}, Best score: {best_score}, Threshold: {threshold}")

    # Jeśli wynik jest powyżej progu, zwróć odpowiednią intencję
    if best_score >= threshold:
        for intent, descriptions in INTENT_DESCRIPTIONS.items():
            if best_label in descriptions:
                return intent

    return "unknown"