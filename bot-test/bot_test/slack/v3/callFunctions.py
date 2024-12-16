from jira import *


def get_tasks_for_today() -> str:
    get_jira_tasks("duedate = now()")
    return "Zadania na dzisiaj:\n" + get_jira_tasks("duedate = now()")


def get_upcoming_tasks() -> str:
    return "Najbliższe zadania:\n1. Prezentacja w poniedziałek\n2. Odpowiedź na e-maile"


def get_tasks_for_week() -> str:
    return "Zadania na ten tydzień:\n1. Warsztaty techniczne\n2. Przegląd projektu"


def get_meetings_for_today() -> str:
    return "Dzisiejsze spotkania na dzisiaj:"


def get_schedule_for_today() -> str:
    return "plan na dzisiaj:"


def get_static_meetings():
    return """Nadchodzące spotkania:
1. 2024-11-21 10:00 - Spotkanie z klientem
2. 2024-11-21 13:00 - Przegląd projektu
3. 2024-11-22 09:00 - Warsztaty techniczne"""
