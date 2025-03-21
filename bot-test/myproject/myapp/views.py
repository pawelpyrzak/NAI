import json
import json
import zipfile
from datetime import timedelta, datetime

import magic
import requests
import unicodedata
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseForbidden
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from jira import JIRA, JIRAError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from trello import TrelloClient

from .decorators import user_belongs_to_group
from .forms import BasicRegistrationForm, ProfileUpdateForm, FileUploadForm, GroupForm, ProjectForm, \
    SearchForm, TaskForm, EventForm, PlatformChannelForm, JiraConfigForm, TaskEditForm, TrelloConfigForm
from .models import GroupMember, Change, Comment, Notification, UserPlatformAccount, Group, \
    JiraConfig, Project, Task, Event, UploadedFile, PlatformChannel, ProjectPlatform, Reminder, TaskIntegration, \
    ProjectExternalKey, TrelloConfig
from .models import Widget
from .serializer import NotificationSerializer, TaskSerializer, EventSerializer
from .utils.bot_logic import get_chatbot_response
from .utils.jira_logic import update_jira_issue, create_jira_issue
from .utils.minio_utils import upload_to_minio, get_file_from_minio, delete_file_from_minio
from .utils.qdrant import search_files_in_group, get_all_files, file_delete, \
    extract_text_from_file, generate_vector_384_from_text, add_to_qdrant, extract_image_embedding
from .utils.trello_logic import create_trello_card, update_trello_card


def greeting_based_on_time():
    current_hour = datetime.now().hour
    if 5 <= current_hour < 18:
        return "Dzień dobry"
    elif 18 <= current_hour or current_hour < 5:
        return "Dobry wieczór"
    else:
        return "Dobranoc"


# Miscellaneous views
@login_required
def homepage(request):
    now = timezone.now()
    user_groups = Group.objects.filter(members__user=request.user)
    today = timezone.localdate()
    start_of_today = datetime.combine(today, datetime.min.time())
    end_of_today = start_of_today + timedelta(days=1)

    events = Event.objects.filter(
        group__in=user_groups,
        start_date__lt=end_of_today,
        end_date__gte=start_of_today
    )

    events2 = Event.objects.filter(
        created_by=request.user,
        start_date__lt=end_of_today,
        end_date__gte=start_of_today
    )
    combined_events = events.union(events2)
    events = list(combined_events.values_list('name', flat=True))
    context = {'csrf_token': get_token(request), 'now': now, 'events': events, "greeting": greeting_based_on_time}
    return render(request, 'myapp/home/home.html', context)


def home(request):
    return render(request, 'myapp/main.html')


# user
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile(request):
    return render(request, 'myapp/profile/profile.html')


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'myapp/login.html')


def register(request):
    if request.method == 'POST' and 'basic_registration' in request.POST:
        form = BasicRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session['user_id'] = user.id
            return redirect('profile_update')

    form = BasicRegistrationForm()
    return render(request, 'myapp/register/register.html', {'form': form, 'step': 1})


def profile_update(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')

    if request.method == 'POST' and 'profile_update' in request.POST:
        user = User.objects.get(id=user_id)
        profile_form = ProfileUpdateForm(request.POST, request.FILES)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            del request.session['user_id']
            login(request, user)
            return redirect('home')

    profile_form = ProfileUpdateForm()
    return render(request, 'myapp/register/register.html', {'profile_form': profile_form, 'step': 2})


# group

@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save()
            GroupMember.objects.create(user=request.user, group=group, role='admin')
            return redirect('teamPage', group_id=group.id)
    else:
        form = GroupForm()
    return render(request, 'myapp/group/teamCreate.html', {'form': form})


@login_required
def team_page(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    return render(request, 'myapp/group/teamPage.html', {'group': group})


@login_required
def join_group(request):
    if request.method == "POST":
        group_code = request.POST.get('join_code')
        if group_code:
            group = get_object_or_404(Group, join_code=group_code)
            if not GroupMember.objects.filter(user=request.user, group=group).exists():
                # Dodaj użytkownika do grupy
                GroupMember.objects.create(user=request.user, group=group, role='member')
                return redirect('teamPage', group_id=group.id)
            else:
                return HttpResponse("Jesteś już członkiem tej grupy.")
        else:
            return HttpResponse("Kod grupy jest wymagany.")
    return render(request, 'myapp/group/teamJoin.html')


@login_required
@user_belongs_to_group
def team_page(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    return render(request, 'myapp/group/teamPage.html', {'group': group})


@login_required
def teams(request):
    groups = GroupMember.objects.filter(user=request.user).select_related('group')
    return render(request, 'myapp/group/groups.html', {'groups': groups})


class GroupInfoView(TemplateView):
    template_name = 'myapp/group/group_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = get_object_or_404(Group, id=kwargs['group_id'])
        context['group'] = group
        context['users'] = group.members.select_related('user')  # Fetch users related to the group
        context['is_member'] = GroupMember.objects.filter(group=group, user=self.request.user).exists()
        return context

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(Group, id=kwargs['group_id'])
        if 'leave_group' in request.POST:
            GroupMember.objects.filter(group=group, user=request.user).delete()
        return redirect('group_info', group_id=group.id)


# projects

@login_required
def create_project(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.group = group
            project.created_by = request.user
            project.save()
            messages.success(request, f"Projekt '{project.name}' został pomyślnie utworzony.")
            return redirect('group_projects', group_id=group.id)
    else:
        form = ProjectForm()

    return render(request, 'myapp/group/create_project.html', {'form': form, 'group': group})


@login_required
def group_projects(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    jira_config = JiraConfig.objects.filter(group=group).first()
    trello_config = TrelloConfig.objects.filter(group=group).first()

    group_projects = Project.objects.filter(group=group)

    jira_project_keys = set(
        ProjectExternalKey.objects.filter(project__group=group, platform__name="Jira").values_list("key", flat=True)
    )

    # Lista projektów Jira
    jira_projects = []
    if jira_config:
        try:
            jira = JIRA(server=jira_config.jira_url, basic_auth=(jira_config.jira_email, jira_config.jira_api_key))
            jira_projects_raw = jira.projects()
            jira_projects = [{'key': project.key, 'name': project.name} for project in jira_projects_raw]
        except Exception as e:
            messages.error(request, f"Błąd podczas komunikacji z Jira: {str(e)}")

    available_jira_projects = [project for project in jira_projects if project['key'] not in jira_project_keys]

    trello_boards = []
    if trello_config:
        try:
            client = TrelloClient(
                api_key=trello_config.api_key,
                token=trello_config.token
            )
            boards = client.list_boards()
            trello_boards = [{'id': board.id, 'name': board.name} for board in boards]
        except Exception as e:
            messages.error(request, f"Błąd podczas komunikacji z Trello: {str(e)}")

    trello_board_ids = set(
        ProjectExternalKey.objects.filter(project__group=group, platform__name="Trello").values_list("key", flat=True)
    )

    available_trello_boards = [board for board in trello_boards if board['id'] not in trello_board_ids]

    return render(request, 'myapp/group/group_projects.html', {
        'group': group,
        'group_projects': group_projects,
        'available_jira_projects': available_jira_projects,
        'available_trello_boards': available_trello_boards,
        'jira_config': jira_config,
        'trello_config': trello_config,
    })


def add_jira_project(request, group_id, jira_project_key):
    group = get_object_or_404(Group, id=group_id)
    jira_config = JiraConfig.objects.filter(group=group).first()

    if not jira_config:
        messages.error(request, "Brak konfiguracji Jira dla tej grupy.")
        return redirect('group_projects', group_id=group.id)

    try:
        jira = JIRA(server=jira_config.jira_url, basic_auth=(jira_config.jira_email, jira_config.jira_api_key))
        project = jira.project(jira_project_key)

        # Sprawdzenie, czy projekt już istnieje w danej grupie
        existing_project_key = ProjectExternalKey.objects.filter(key=project.key, platform__name="Jira").first()
        if existing_project_key:
            existing_project = existing_project_key.project
            existing_project.name = project.name
            existing_project.description = project.description or ""
            existing_project.save()
            messages.success(request, f"Projekt '{project.name}' został zaktualizowany w grupie.")

        else:
            # Tworzenie nowego projektu
            new_project = Project.objects.create(
                name=project.name,
                description=project.description or "",
                group=group,
                created_by=request.user,
                project_menager=request.user
            )

            # Pobranie platformy Jira i utworzenie wpisu w ProjectExternalKey
            jira_platform, _ = ProjectPlatform.objects.get_or_create(name="Jira")
            ProjectExternalKey.objects.create(project=new_project, platform=jira_platform, key=project.key)

            messages.success(request, f"Projekt '{project.name}' został dodany do grupy.")

    except JIRAError as e:
        messages.error(request, f"Błąd Jira: {str(e)}")
    except Exception as e:
        messages.error(request, f"Wystąpił nieoczekiwany błąd: {str(e)}")

    return redirect('group_projects', group_id=group.id)


def posts_content(request):
    return render(request, 'myapp/groups/feed.html')


# project
def projects(request):
    today = timezone.now().date()
    user_groups = GroupMember.objects.filter(user=request.user).values_list('group', flat=True)
    projects_list = Project.objects.filter(group__in=user_groups)

    def add_dynamic_data(projects_list):
        for project in projects_list:
            tasks = project.tasks
            project.managerName = f"{project.project_manager.profile.first_name} {project.project_manager.profile.last_name}"
            project.managerImg = project.project_manager.profile.profile_image.url
            project.days_left = (project.due_date - today).days
            project.participants = project.group.members.all()

            project.attachments_count = project.tasks.aggregate(total_attachments=Count('attachments'))[
                'total_attachments']
            project.completed_tasks = tasks.filter(status='completed')
            project.tasks_in_progress = tasks.filter(status='in_progress')
            project.upcomingTasks = tasks.filter(due_date__gt=today)
            project.progres = 0
            project.created_tasks = tasks.count()
            if tasks.count() > 0:
                progress = (project.completed_tasks.count() / tasks.count()) * 100
                project.progress = int(progress)
            print(project.participants)
        return projects_list

    in_progress = add_dynamic_data(projects_list.filter(status="In_progres"))
    pending = add_dynamic_data(projects_list.filter(status="Pending"))
    completed = add_dynamic_data(projects_list.filter(status="Completed"))
    at_risk = add_dynamic_data(projects_list.filter(status="At_risk"))

    return render(request, 'myapp/projects/projects.html',
                  {'in_progress': in_progress, 'pending': pending, 'completed': completed, 'at_risk': at_risk, })


def projects_board(request):
    return render(request, 'myapp/projects/projects-board.html')


@login_required
def project(request, project_id):
    today = timezone.now().date()
    project = get_object_or_404(Project, id=project_id)
    changes = Change.objects.filter(project=project).order_by('-date_changed')
    if not project.project_manager:
        project.project_manager=project.created_by
    project.managerName = f"{project.project_manager.profile.first_name} {project.project_manager.profile.last_name}"
    project.managerImg = project.project_manager.profile.profile_image.url
    if project.due_date:
        project.days_left = (project.due_date - today).days
    else:
        project.days_left=7
    project.participants = [member.user.profile for member in project.group.members.all()]
    project.attachments_count = project.tasks.aggregate(total_attachments=Count('attachments'))['total_attachments']
    project.completed_tasks = project.tasks.filter(status='completed')
    project.tasks_in_progress = project.tasks.filter(status='in_progress')
    project.upcomingTasks = project.tasks.filter(due_date__gt=today)

    project.created_tasks = project.tasks.count()
    task_list = Task.objects.filter(project=project)

    task_groups = {
        "Przeterminowane": [],
        "W tym tygodniu": [],
        "W tym miesiącu": [],
        "Reszta": []
    }

    for task in task_list:
        changes = Change.objects.filter(task=task)
        task.changes.set(changes)
        task.days_left = (task.due_date - today).days

        if task.days_left < 0:
            task_groups["Przeterminowane"].append(task)
            task.days_left = abs(task.days_left)
        elif 0 <= task.days_left <= 7:
            task_groups["W tym tygodniu"].append(task)
        elif 7 < task.days_left <= 30:
            task_groups["W tym miesiącu"].append(task)
        else:
            task_groups["Reszta"].append(task)
    task_groups["Przeterminowane"].sort(key=lambda x: x.days_left, reverse=True)

    project.progress = 0
    if project.tasks.count() > 0:
        project.progress = (project.completed_tasks.count() / project.tasks.count()) * 100
        project.progres = min(project.progress, 100)
    delay = False
    if project.days_left < 0:
        delay = True
        project.days_left = abs(project.days_left)

    return render(request, 'myapp/projects/project.html',
                  {'project': project, 'delay': delay, 'changes': changes, 'task_list': task_list,
                   "form": ProjectForm(), 'task_groups': task_groups})


# calendar

@login_required
def calendar(request):
    if request.method == 'POST':
        content = request.POST.get('view-selector')
        if content:
            return render(request, 'myapp/calendar/calendar.html', {'calendar': content})
    return render(request, 'myapp/calendar/calendar.html', {'calendar': "Month"})


@login_required
def event_list(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    events = Event.objects.filter(group=group).order_by('start_date')
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.group = group
            event.created_by = request.user
            event.save()
            return redirect('event_list', group_id=group.id)
    else:
        form = EventForm()

    return render(request, 'myapp/event/events.html', {'events': events, 'group': group, 'form': form, })


# Task views
@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tasks')  # Redirect to tasks list (replace 'tasks' with actual URL name)
    else:
        form = TaskForm()
    return render(request, 'myapp/task/create_task.html', {'form': form})


class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


@login_required
def tasks(request):
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)

    not_done_tasks = Task.objects.exclude(status="completed")

    to_do_today = not_done_tasks.filter(due_date=today)
    to_do_tomorrow = not_done_tasks.filter(due_date=tomorrow)
    to_do_this_week = not_done_tasks.filter(due_date__gte=today, due_date__lt=next_week)
    overdue = not_done_tasks.filter(due_date__lt=today)

    def add_dynamic_data(tasks):
        for task in tasks:
            days_left = (task.due_date - today).days
            participants_count = 1 if task.assignee else 0
            attachments_count = task.attachments.count()
            if task.assignee:
                task.managerName = task.assignee.profile.full_name
                task.managerImg = task.assignee.profile.profile_image.url
            task.days_left = days_left
            task.participants_count = participants_count
            task.attachments_count = attachments_count
        return tasks

    to_do_today = add_dynamic_data(to_do_today)
    to_do_tomorrow = add_dynamic_data(to_do_tomorrow)
    to_do_this_week = add_dynamic_data(to_do_this_week)
    overdue = add_dynamic_data(overdue)

    return render(request, 'myapp/task/tasks.html',
                  {'to_do_today': to_do_today, 'to_do_tomorrow': to_do_tomorrow, 'to_do_this_week': to_do_this_week,
                   'overdue': overdue, })


def singleTask(request, task_id):
    today = timezone.now().date()
    task = get_object_or_404(Task, id=task_id)
    comments = Comment.objects.filter(task=task, parent__isnull=True).order_by('-created_at')
    reply = Comment.objects.filter(task=task, parent__isnull=False).order_by('-created_at')

    task.days_left = (task.due_date - today).days
    delay = False
    if task.days_left < 0:
        delay = True
        task.days_left = abs(task.days_left)

    can_edit = request.user == task.assignee or request.user == task.task_manager

    messages_list = messages.get_messages(request)
    form = TaskEditForm(project=task.project)
    return render(request, 'myapp/task/singleTask.html', {
        'task': task,
        'comments': comments,
        'reply': reply,
        'delay': delay,
        'form': form,
        'can_edit': can_edit,
        'messages': messages_list
    })


@login_required
def add_comment(request, task_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            return redirect('singleTask', task_id=task_id)
        task = Task.objects.get(id=task_id)
        comment = Comment.objects.create(content=content, author=request.user, task=task)
        comment.save()
    return redirect('singleTask', task_id=task_id)


@login_required
def add_reply(request, task_id, comment_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            return redirect('singleTask', task_id=task_id)
        comment = Comment.objects.get(id=comment_id)
        reply = Comment.objects.create(content=content, author=request.user, task=comment.task, parent=comment)
        reply.save()

    return redirect('singleTask', task_id=task_id)


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def get_queryset(self):
        user_groups = Group.objects.filter(members__user=self.request.user)
        return Event.objects.filter(group__in=user_groups)


# # notification
# @login_required
# def reminders_page(request):
#     if request.method == 'POST':
#         form = ReminderForm(request.POST)
#         if form.is_valid():
#             reminder = form.save(commit=False)
#             reminder.user = request.user
#             reminder.save()
#             return redirect('reminders_page')
#     else:
#         form = ReminderForm()
#
#     reminders = Reminder.objects.filter(user=request.user)
#     return render(request, 'myapp/reminder/reminders_page.html', {'form': form, 'reminders': reminders})
#

class NotificationListView(APIView):
    def get(self, request):
        notifications = Notification.objects.all()
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": count})

    @action(detail=False, methods=['get'], url_path='all')
    def all_notifications(self, request):
        notifications = self.get_queryset()
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_notification(self, request, pk=None):
        notification = self.get_object()
        notification.delete()
        return Response({'status': 'notification deleted'}, status=204)


# files
def detect_office_mime(file):
    try:
        file.seek(0)
        with zipfile.ZipFile(file, 'r') as archive:
            files = archive.namelist()
            if "word/document.xml" in files:
                return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif "xl/workbook.xml" in files:
                return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif "ppt/presentation.xml" in files:
                return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            else:
                return None
    except zipfile.BadZipFile:
        return None


def get_mime_type(file):
    file.seek(0)
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file.read(1024))
    file.seek(0)
    return mime_type


@login_required
def manage_files(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group_member = get_object_or_404(GroupMember, user=request.user, group=group)

    upload_form = FileUploadForm()
    search_form = SearchForm()
    results = get_all_files(group_id)
    all_files = True

    if request.method == "POST":
        # Sprawdzenie, który formularz został wysłany
        if "upload" in request.POST:  # Jeśli kliknięto "Prześlij plik"
            upload_form = FileUploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                file = upload_form.cleaned_data['file']
                if not file:
                    messages.error(request, 'Plik nie został przesłany')
                    return redirect('manage_files', group_id=group_id)

                mime_type = get_mime_type(file)
                if mime_type.startswith("image/"):
                    vector = extract_image_embedding(file)
                else:
                    if mime_type == "application/zip":
                        mime_type = detect_office_mime(file)
                    extracted_text = extract_text_from_file(file, mime_type)

                    if extracted_text is None:
                        messages.error(request, 'Nieobsługiwany typ pliku')
                        return redirect('manage_files', group_id=group_id)

                    vector = generate_vector_384_from_text(extracted_text)

                file.seek(0)
                file_name = file.name
                bucket_name, file_path = upload_to_minio(file, group_id)
                file_uuid = add_to_qdrant(vector, bucket_name, file_path, file_name, mime_type.startswith("image/"))

                if not file_uuid:
                    delete_file_from_minio(group_id, file_path)
                    messages.error(request, 'Nie udało się dodać pliku do Qdrant. Plik został usunięty.')
                    return redirect('manage_files', group_id=group_id)

                UploadedFile.objects.create(
                    name=file_name, group=group, qdrant_id=file_uuid, mime_type=mime_type, minio_path=file_path
                )
                messages.success(request, "Plik został przesłany.")
                return redirect('manage_files', group_id=group_id)

        elif "search" in request.POST:  # Jeśli kliknięto "Szukaj"
            search_form = SearchForm(request.POST)
            if search_form.is_valid():
                query = search_form.cleaned_data['query']
                group_files = UploadedFile.objects.filter(group_id=group_id)
                ids = [file.qdrant_id for file in group_files]
                results = search_files_in_group(query, ids, len(ids))
                for result in results:
                    result.score = result.score * 100
                all_files = False

    return render(request, "myapp/files/manage_files.html", {
        "upload_form": upload_form,
        "search_form": search_form,
        "results": results,
        "group": group,
        "all_files": all_files,
        "group_member": group_member,
    })


@login_required
def upload_file(request, group_id):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            if not file:
                messages.error(request, 'Plik nie został przesłany')
                return render(request, "myapp/files/upload_file.html", {"form": form, "group_id": group_id})

            group = get_object_or_404(Group, id=group_id)

            mime_type = get_mime_type(file)
            if mime_type.startswith("image/"):
                vector = extract_image_embedding(file)
            else:
                if mime_type == "application/zip":
                    mime_type = detect_office_mime(file)
                extracted_text = extract_text_from_file(file, mime_type)

                if extracted_text is None:
                    messages.error(request, 'Nieobsługiwany typ pliku')
                    return render(request, "myapp/files/upload_file.html", {"form": form, "group_id": group_id})

                vector = generate_vector_384_from_text(extracted_text)

            file.seek(0)
            file_name = file.name
            bucket_name, file_path = upload_to_minio(file, group_id)
            file_uuid = add_to_qdrant(vector, bucket_name, file_path, file_name, mime_type.startswith("image/"))

            if not file_uuid:
                delete_file_from_minio(group_id, file_path)
                messages.error(request, 'Nie udało się dodać pliku do Qdrant. Plik został usunięty.')
                return render(request, "myapp/files/upload_file.html", {"form": form, "group_id": group_id})

            UploadedFile.objects.create(name=file_name, group=group, qdrant_id=file_uuid, mime_type=mime_type,
                                        minio_path=file_path)
            return redirect('search_files', group_id=group_id)
        else:
            messages.error(request, 'Form error')
            return render(request, "myapp/files/upload_file.html", {"form": form, "group_id": group_id})

    else:
        form = FileUploadForm()

    return render(request, "myapp/files/upload_file.html", {"form": form, "group_id": group_id})


@login_required
def delete_file(request, group_id, file_uuid):
    group = get_object_or_404(Group, id=group_id)
    file = get_object_or_404(UploadedFile, qdrant_id=file_uuid, group=group)
    group_member = get_object_or_404(GroupMember, user=request.user, group=group)

    if group_member.role == 'admin':
        file_delete(file.qdrant_id)
        delete_file_from_minio(file.group.id, file.minio_path)
        file.delete()

        # Wyświetlamy komunikat o sukcesie
        messages.success(request, 'Plik został pomyślnie usunięty.')
        return redirect('search_files', group_id=group.id)
    else:
        messages.error(request, 'Nie masz uprawnień do usuwania tego pliku.')
        return redirect('search_files', group_id=group.id)


@login_required
def download_file(request, qdrant_id):
    try:
        file = get_object_or_404(UploadedFile, qdrant_id=qdrant_id)
        file_stream = get_file_from_minio(file)
        response = StreamingHttpResponse(file_stream, content_type=file.mime_type)
        response['Content-Disposition'] = f'attachment; filename="{file.name}"; filename*=UTF-8''{file.name}'
        return response

    except FileNotFoundError as e:
        return HttpResponse(str(e), status=404)


@login_required
def search_files(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group_member = get_object_or_404(GroupMember, user=request.user, group=group)

    all_files = True
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            group_files = UploadedFile.objects.filter(group_id=group_id)
            ids = [file.qdrant_id for file in group_files]
            results = search_files_in_group(query, ids, len(ids))
            for result in results:
                result.score = result.score * 100
            all_files = False
    else:
        form = SearchForm()
        results = get_all_files(group_id)
    get_all_files(group_id)
    return render(request, "myapp/files/search_files.html",
                  {"form": form, "results": results, "group": group, "all_files": all_files,
                   "group_member": group_member})


def view_platforms(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    jira_config = JiraConfig.objects.filter(group=group).first()
    trello_config = TrelloConfig.objects.filter(group=group).first()

    channel_form = PlatformChannelForm()
    jira_form = JiraConfigForm()
    trello_form= TrelloConfigForm()
    channels = PlatformChannel.objects.filter(group=group_id)
    if request.method == 'POST':
        # Dodawanie kanału
        if 'add_channel' in request.POST:
            channel_form = PlatformChannelForm(request.POST)
            if channel_form.is_valid():
                channel = channel_form.save(commit=False)
                channel.group = group
                channel.save()
                messages.success(request, "Kanał został dodany pomyślnie.")
                return redirect('group_platforms', group_id=group.id)

        # Usuwanie konfiguracji Jira
        elif 'delete_jira' in request.POST:
            if jira_config:
                jira_config.delete()
                messages.success(request, "Konfiguracja Jira została usunięta.")
            return redirect('group_platforms', group_id=group.id)

        # Dodawanie konfiguracji Jira
        elif 'add_jira' in request.POST:
            jira_form = JiraConfigForm(request.POST)
            if jira_form.is_valid():
                jira = jira_form.save(commit=False)
                jira.group = group
                jira.save()
                messages.success(request, "Konfiguracja Jira została dodana.")
                return redirect('group_platforms', group_id=group.id)
        elif 'delete_trello' in request.POST:
            if trello_config:
                trello_config.delete()
                messages.success(request, "Konfiguracja Trello została usunięta.")
            return redirect('group_platforms', group_id=group.id)
        elif 'add_trello' in request.POST:
            trello_form = TrelloConfig(request.POST)
            if trello_form.is_valid():
                trello = trello_form.save(commit=False)
                trello.group = group
                trello.save()
                messages.success(request, "Konfiguracja Trello została dodana.")
                return redirect('group_platforms', group_id=group.id)

    context = {'group': group, 'channel_form': channel_form,
               'jira_config': jira_config, 'jira_form': jira_form,'trello_config': trello_config, 'trello_form': trello_form, 'channels': channels}

    return render(request, 'myapp/group/group_platforms.html', context)


# łączenie jira i user
@login_required
def jira_user_match(request, group_id):
    try:
        group = get_object_or_404(Group, id=group_id)
        jira_config = get_object_or_404(JiraConfig, group=group)
        auth = (jira_config.jira_email, jira_config.jira_api_key)
        headers = {'Content-Type': 'application/json', }
        url = f"{jira_config.jira_url}/rest/api/2/users"
        response = requests.get(url, auth=auth, headers=headers)

        if response.status_code != 200:
            raise ValueError(f"Błąd połączenia z JIRA: {response.status_code} - {response.text}")

        jira_users = response.json()
        filtered_users = [user for user in jira_users if user.get("accountType") != "app"]
        jira_platform = ProjectPlatform.objects.filter(name="Jira").first()

        user_account = UserPlatformAccount.objects.filter(user=request.user, platform=jira_platform).first()
        if user_account:
            return render(request, "myapp/group/jira_user_match.html", {"user_account": user_account})

        full_name = request.user.profile.full_name()
        matched_users = [user for user in filtered_users if
                         user.get('displayName') == full_name or user.get('displayName') == request.user.username]

        # Dodanie logiki: jeśli użytkownik ma już przypisane UserPlatformAccount z jira_id, nie dodawaj go do matched_users
        existing_jira_account_ids = UserPlatformAccount.objects.filter(platform=jira_platform).values_list(
            'platform_user_id', flat=True)
        matched_users = [user for user in matched_users if user.get('accountId') not in existing_jira_account_ids]

        for user in matched_users:
            user['avatar_url'] = user['avatarUrls'].get('48x48', None)

        return render(request, "myapp/group/jira_user_match.html",
                      {"matched_users": matched_users, "group_id": group_id, "user_account": None, })

    except ValueError as e:
        print(e)
        messages.error(request, str(e))
        return redirect('jira_user_match', group_id=group_id)


@login_required
def trello_user_match(request, group_id):
    try:
        group = get_object_or_404(Group, id=group_id)
        trello_config = get_object_or_404(TrelloConfig, group=group)
        trello_platform = ProjectPlatform.objects.filter(name="Trello").first()

        project_keys = ProjectExternalKey.objects.filter(project__group=group, platform=trello_platform)
        trello_users = []

        for project_key in project_keys:
            if not project_key.key:
                continue

            url = f"https://api.trello.com/1/boards/{project_key.key}/members?key={trello_config.trello_api_key}&token={trello_config.trello_oauth_token}"
            response = requests.get(url)

            if response.status_code != 200:
                raise ValueError(
                    f"Błąd połączenia z Trello dla projektu {project_key.project.name}: {response.status_code} - {response.text}")

            trello_users.extend(response.json())

        trello_users = {user["id"]: user for user in trello_users}.values()  # Usunięcie duplikatów

        user_account = UserPlatformAccount.objects.filter(user=request.user, platform=trello_platform).first()
        if user_account:
            return render(request, "myapp/group/trello_user_match.html", {"user_account": user_account})

        full_name = request.user.profile.full_name()
        matched_users = [user for user in trello_users if
                         user.get("fullName") == full_name or user.get("username") == request.user.username]

        existing_trello_account_ids = UserPlatformAccount.objects.filter(platform=trello_platform).values_list(
            'platform_user_id', flat=True)

        matched_users = [user for user in matched_users if user.get("id") not in existing_trello_account_ids]

        for user in matched_users:
            user["avatar_url"] = user.get("avatarUrl")

        return render(request, "myapp/group/trello_user_match.html",
                      {"matched_users": matched_users, "group_id": group_id, "user_account": None})

    except ValueError as e:
        print(e)
        messages.error(request, str(e))
        return redirect('trello_user_match', group_id=group_id)


@login_required
@require_POST
def link_jira_user(request, group_id, jira_user_id):
    try:
        if not isinstance(group_id, int) or not jira_user_id:
            raise ValueError("Invalid group ID or JIRA user ID.")

        user_profile = request.user.profile
        django_user_full_name = f"{user_profile.first_name} {user_profile.last_name}"

        jira_platform = ProjectPlatform.objects.filter(name="Jira").first()

        if UserPlatformAccount.objects.filter(user=request.user, platform=jira_platform,
                                              platform_user_id=jira_user_id).exists():
            messages.warning(request, "Twoje konto jest już połączone z tym użytkownikiem JIRA.", )
        else:
            UserPlatformAccount.objects.create(user=request.user, platform=jira_platform,
                                               username=django_user_full_name, platform_user_id=jira_user_id, )
            messages.success(request, "Połączono Twoje konto z JIRA.")

    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, "Wystąpił błąd podczas łączenia konta z JIRA.")
    return redirect("jira_user_match", group_id=group_id)

@login_required
@require_POST
def link_trello_user(request, group_id, trello_user_id):
    try:
        if not isinstance(group_id, int) or not trello_user_id:
            raise ValueError("Invalid group ID or Trello user ID.")

        user_profile = request.user.profile
        django_user_full_name = f"{user_profile.first_name} {user_profile.last_name}"

        trello_platform = ProjectPlatform.objects.filter(name="Trello").first()

        if UserPlatformAccount.objects.filter(user=request.user, platform=trello_platform,
                                              platform_user_id=trello_user_id).exists():
            messages.warning(request, "Twoje konto jest już połączone z tym użytkownikiem Trello.", )
        else:
            UserPlatformAccount.objects.create(user=request.user, platform=trello_platform,
                                               username=django_user_full_name, platform_user_id=trello_user_id, )
            messages.success(request, "Połączono Twoje konto z Trello.")

    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, "Wystąpił błąd podczas łączenia konta z Trello.")
    return redirect("trello_user_match", group_id=group_id)

# Bot communication view
def normalize_text(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if
                   unicodedata.category(c) != 'Mn').lower()  # Zamienia na małe litery


@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # user_input = normalize_text(data.get("message", ""))
        user_input = normalize_text(data.get("message", ""))

        print(user_input)
        response = get_chatbot_response(user_input, request)

        return JsonResponse({"response": response})


def fetch_slack_user_details(api_key, user_id):
    client = WebClient(token=api_key)
    try:
        response = client.users_info(user=user_id)
        return response["user"]
    except SlackApiError:
        return {}


def fetch_slack_messages(channel_id):
    from decouple import config
    api_key = config("SLACK_BOT_TOKEN")

    client = WebClient(token=api_key)
    try:
        response = client.conversations_history(channel=channel_id, limit=10)
        messages = response["messages"]
        formatted_messages = []

        for msg in messages:
            user_id = msg.get("user")  # ID użytkownika
            user_details = fetch_slack_user_details(api_key, user_id) if user_id else None

            formatted_messages.append({
                "content": msg.get("text", ""),
                "timestamp": msg.get("ts", ""),
                "author": {
                    "name": user_details.get("real_name",
                                             "Nieznany użytkownik") if user_details else "Nieznany użytkownik",
                    "avatar_url": user_details.get("profile", {}).get("image_48") if user_details else None,
                }
            })

        return formatted_messages
    except SlackApiError as e:
        return [{"error": str(e)}]


def fetch_discord_messages(channel_id):
    from decouple import config
    import requests

    api_key = config("DISCORD_TOKEN")

    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {api_key}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        messages = response.json()

        # Ograniczenie do 10 ostatnich wiadomości
        messages = messages[:10]

        formatted_messages = []

        for msg in messages:
            author = msg.get("author", {})
            formatted_messages.append({
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp", ""),
                "author": {
                    "name": author.get("username", "Nieznany użytkownik"),
                    "avatar_url": f"https://cdn.discordapp.com/avatars/{author.get('id')}/{author.get('avatar')}.png" if author.get(
                        "avatar") else None,
                }
            })

        return formatted_messages
    except requests.RequestException as e:
        return [{"error": str(e)}]


def get_messages(group_id, platform_name):
    group = get_object_or_404(Group, id=group_id)

    channels = PlatformChannel.objects.filter(platform__name__iexact=platform_name, group=group)

    all_messages = []

    for channel in channels:
        if platform_name == "Slack":
            messages = fetch_slack_messages(channel.channel_id)
        if platform_name == "Discord":
            messages = fetch_discord_messages(channel.channel_id)
        all_messages.append({
            "channel_name": channel.name,
            "messages": messages,
            "platform_name": platform_name,
        })
    return all_messages


def slack_messages_view(request, group_id):
    all_messages = get_messages(group_id, "Slack")
    return render(request, "myapp/group/messages.html", {"all_messages": all_messages})


def discord_messages_view(request, group_id):
    all_messages = get_messages(group_id, "Discord")
    return render(request, "myapp/group/messages.html", {"all_messages": all_messages})


def messages_view(request, group_id):
    all_messages = []
    all_messages.extend(get_messages(group_id, "Discord"))
    all_messages.extend(get_messages(group_id, "Slack"))
    return render(request, "myapp/group/messages.html", {"all_messages": all_messages})


def load_reminder_content(request, view_type):
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    user_reminders = Reminder.objects.filter(user=request.user)
    template = 'myapp/home/widget/reminder-widget-today.html'
    if view_type == 'today':
        reminders = user_reminders.filter(time__gte=today)
    elif view_type == 'tomorrow':
        reminders = user_reminders.filter(time__gte=tomorrow)
    elif view_type == 'week':
        reminders = user_reminders.filter(time__gte=today, time__lt=next_week)
    elif view_type == 'all':
        reminders = user_reminders.filter(time__gte=today)
    else:
        reminders = user_reminders
    # Renderowanie szablonu
    html_content = render(request, template, context={'reminders': reminders})

    return JsonResponse({'html': html_content.content.decode()})


def get_calendar_widget(request):
    return render(request, 'myapp/home/widget/calendar-widget.html')


def load_project_content(request, view_type):
    today = timezone.now().date()
    user_groups = GroupMember.objects.filter(user=request.user).values_list('group', flat=True)
    projects_list = Project.objects.filter(group__in=user_groups)

    def add_dynamic_data(projects_list):
        for project in projects_list:
            tasks = project.tasks
            project.participants = project.group.members.all()
            project.attachments_count = project.tasks.aggregate(total_attachments=Count('attachments'))[
                'total_attachments']
            project.completed_tasks = tasks.filter(status='completed')
            project.progress = 0
            if tasks.count() > 0:
                progress = (project.completed_tasks.count() / tasks.count()) * 100
                project.progress = int(progress)
        return projects_list

    template = 'myapp/home/widget/project_list-widget.html'
    if view_type == 'in-progress':
        projects = add_dynamic_data(projects_list.filter(status="In_progres"))
    elif view_type == 'pending':
        projects = add_dynamic_data(projects_list.filter(status="Pending"))
    elif view_type == 'at_risk':
        projects = add_dynamic_data(projects_list.filter(status="At_risk"))
    elif view_type == 'completed':
        projects = add_dynamic_data(projects_list.filter(status="Completed"))
    else:
        # projects = add_dynamic_data(projects_list.filter(status="In_progres"))
        projects = add_dynamic_data(projects_list.filter(status="Pending"))
    context = {'projects': projects}
    html_content = render(request, template, context)

    return JsonResponse({'html': html_content.content.decode()})


def load_task_content(request, view_type):
    today = timezone.now().date()
    tasks = Task.objects.filter(assignee=request.user)
    overdue_f = tasks.exclude(due_date__lt=today)
    to_do = overdue_f.filter(status="Do zrobienia")
    in_progres = overdue_f.filter(status="W toku")
    overdue = tasks.filter(due_date__lt=today).exclude(status="completed")
    completed = tasks.filter(status="completed")
    template = 'myapp/home/widget/taskToDoWidget.html'
    if view_type == 'in-progress':
        tasks = in_progres
    elif view_type == 'overdue':
        tasks = overdue
    elif view_type == 'completed':
        tasks = completed
    else:
        tasks = to_do
    html_content = render(request, template, context={'tasks': tasks})

    return JsonResponse({'html': html_content.content.decode()})


def get_statistics(request):
    period = request.GET.get("period", "today")  # Domyślnie "today"

    today = timezone.now().date()

    if period == "today":
        completed_tasks = Task.objects.filter(status="completed", due_date=today)
        to_do_tasks = Task.objects.exclude(status="completed").filter(due_date=today)
    elif period == "this-week":
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        completed_tasks = Task.objects.filter(status="completed", due_date__range=[start_of_week, end_of_week])
        to_do_tasks = Task.objects.exclude(status="completed").filter(due_date__range=[start_of_week, end_of_week])
    elif period == "this-month":
        completed_tasks = Task.objects.filter(status="completed", due_date__month=today.month,
                                              due_date__year=today.year)
        to_do_tasks = Task.objects.exclude(status="completed").filter(due_date__month=today.month,
                                                                      due_date__year=today.year)
    else:
        completed_tasks = Task.objects.filter(status="completed", due_date=today)
        to_do_tasks = Task.objects.exclude(status="completed").filter(due_date=today)
    return JsonResponse({
        "completed_tasks": completed_tasks.count(),
        "to_do_tasks": to_do_tasks.count(),
    })


@login_required
def edit_task(request, task_id):
    print("edit")

    if request.method == "POST":
        print("post")
        task_db = get_object_or_404(Task, id=task_id)
        task_form = TaskEditForm(request.POST)
        if request.user != task_db.assignee and request.user != task_db.task_manager:
            messages.error(request, "❌ Nie masz uprawnień do edycji tego zadania!")
            return HttpResponseForbidden("Nie masz uprawnień do edycji tego zadania.")

        if task_form.is_valid():
            print("valid")
            updated_task = task_form.save(commit=False)
            updated = False
            jira_updates = {}
            trello_updates = {}

            # Aktualizacja tytułu
            if updated_task.title and updated_task.title != task_db.title:
                task_db.title = updated_task.title
                jira_updates["summary"] = updated_task.title
                jira_updates["name"] = updated_task.title

                print("update: title")
                updated = True

            # Aktualizacja opisu
            if updated_task.description and updated_task.description != task_db.description:
                task_db.description = updated_task.description
                jira_updates["description"] = updated_task.description
                trello_updates["desc"] = updated_task.description
                print("update: description")
                updated = True

            # Aktualizacja statusu
            if updated_task.status and updated_task.status != task_db.status:
                task_db.status = updated_task.status
                jira_updates["status"] = {"name": updated_task.status}
                trello_updates["status"] = updated_task.status
                print("update: status")
                updated = True

            # Ustawienie start_date
            current_start_date = task_db.start_date

            if updated_task.start_date and updated_task.start_date >= (task_db.start_date or datetime.min.date()):
                current_start_date = updated_task.start_date
                task_db.start_date = updated_task.start_date
                jira_updates["start_date"] = updated_task.start_date.isoformat()
                trello_updates["start"] = updated_task.start_date.isoformat()
                print("update: start_date")
                updated = True

            # Sprawdzenie due_date
            if updated_task.due_date and updated_task.due_date > (task_db.due_date or datetime.min.date()):
                if current_start_date and updated_task.due_date <= current_start_date:
                    messages.error(request, "❌ Błąd: Due date musi być późniejszy niż start date!")
                    return redirect('singleTask', task_id=task_id)
                else:
                    task_db.due_date = updated_task.due_date
                    jira_updates["duedate"] = updated_task.due_date.isoformat()
                    trello_updates["due"] = updated_task.due_date.isoformat()
                    print("update: due_date")
                    updated = True

            # Aktualizacja priorytetu
            if updated_task.priority and updated_task.priority != task_db.priority:
                task_db.priority = updated_task.priority
                jira_updates["priority"] = {"name": updated_task.priority}
                print("update: priority")
                updated = True

            # Aktualizacja assignee
            if updated_task.assignee and updated_task.assignee != task_db.assignee:
                for platform_name in ["Jira", "Trello"]:
                    platform = ProjectPlatform.objects.filter(name=platform_name).first()
                    user_platform_account = UserPlatformAccount.objects.filter(user=updated_task.assignee,
                                                                               platform=platform).first()
                    if not user_platform_account:
                        messages.error(request,
                                       f"❌ Błąd: Użytkownik {updated_task.assignee} nie ma konta w {platform_name}!")
                        return redirect('singleTask', task_id=task_id)

                    if platform_name in ["Jira", "Trello"]:
                        jira_updates["customfield_10015"] = {"accountId": user_platform_account.platform_user_id}
                    elif platform_name == "Trello":
                        trello_updates["idMembers"] = user_platform_account.platform_user_id

                task_db.assignee = updated_task.assignee
                print(f"update: assignee")
                updated = True

            if updated:
                task_db.save()

                for integration in task_db.integrations.all():
                    if integration.platform.name == "Jira" and integration.key:
                        response = update_jira_issue(task_db, jira_updates)
                        if response.status_code != 204:
                            messages.error(request, f"❌ Błąd aktualizacji Jira: {response.status_code} {response.text}")
                            return redirect('singleTask', task_id=task_id)
                    elif integration.platform.name == "Trello" and integration.key:
                        response = update_trello_card(integration.key, trello_updates)
                        if response.status_code != 204:
                            messages.error(request,
                                           f"❌ Błąd aktualizacji Trello: {response.status_code} {response.text}")
                            return redirect('singleTask', task_id=task_id)

                messages.success(request, "✅ Zadanie zostało pomyślnie zaktualizowane!")
            else:
                messages.info(request, "ℹ️ Nie wprowadzono żadnych zmian.")

    return redirect('singleTask', task_id=task_id)


@login_required
def create_task_view(request):
    if request.method == "POST":
        form = TaskForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.task_manager = request.user
            today = timezone.now().date()
            jira_config = None
            trello_config = None

            if task.start_date and task.start_date < today:
                form.add_error("start_date", "Data rozpoczęcia nie może być wcześniejsza niż dzisiaj.")

            if task.start_date and task.due_date and task.due_date < task.start_date:
                form.add_error("due_date", "Termin realizacji nie może być wcześniejszy niż data rozpoczęcia.")

            if not task.assignee:
                task.assignee = request.user

            platforms = ["Jira", "Trello"]
            for platform_name in platforms:
                if task.project and task.project.integrations.filter(platform__name=platform_name).exists():
                    platform = ProjectPlatform.objects.filter(name=platform_name).first()
                    user_platform_account = UserPlatformAccount.objects.filter(user=task.assignee,
                                                                               platform=platform).first()
                    if not user_platform_account:
                        form.add_error("assignee", f"Przypisany użytkownik musi mieć konto {platform_name} w systemie.")
                    else:
                        if platform_name == "Jira":
                            jira_config = user_platform_account
                        elif platform_name == "Trello":
                            trello_config = user_platform_account

            if not form.errors:
                if jira_config:
                    jira_key, jira_user_id = create_jira_issue(task, jira_config)
                    if jira_key:
                        TaskIntegration.objects.create(task=task, platform=ProjectPlatform.objects.get(name="Jira"),
                                                       external_id=jira_key, external_user_id=jira_user_id)
                    else:
                        form.add_error("project", "Nie udało się dodać zadania do Jira.")

                if trello_config:
                    trello_card_id, trello_user_id = create_trello_card(task, trello_config)
                    if trello_card_id:
                        TaskIntegration.objects.create(task=task, platform=ProjectPlatform.objects.get(name="Trello"),
                                                       external_id=trello_card_id, external_user_id=trello_user_id)
                    else:
                        form.add_error("project", "Nie udało się dodać zadania do Trello.")

                if not form.errors:
                    task.save()
                    return redirect('singleTask', task_id=task.id)
    else:
        form = TaskForm(user=request.user)
    return render(request, 'myapp/task/create_task.html', {'form': form})


@login_required
def edit_project(request, project_id):
    if request.method == "POST":
        project_db = get_object_or_404(Project, id=project_id)
        project_form = ProjectForm(request.POST)

        if project_form.is_valid():
            updated_project = project_form.save(commit=False)
            updated = False

            if updated_project.name and updated_project.name != project_db.name:
                project_db.name = updated_project.name
                print("update: name")
                updated = True

            if updated_project.description and updated_project.description != project_db.description:
                project_db.description = updated_project.description
                print("update: description")
                updated = True

            if updated_project.status and updated_project.status != project_db.status:
                project_db.status = updated_project.status
                print("update: status")
                updated = True

            if updated_project.due_date and updated_project.due_date > (project_db.due_date or datetime.min):
                project_db.due_date = updated_project.due_date
                print("update: due_date")
                updated = True

            if updated:
                project_db.save()

    return redirect('project', project_id=project_id)


@csrf_exempt
@login_required
def update_widget_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_list = data.get("order", [])

            if not order_list:
                return JsonResponse({"error": "Brak danych dotyczących kolejności widgetów."}, status=400)

            # Walidacja: każdy element musi zawierać "id", "position" oraz "size"
            positions_set = set()
            for item in order_list:
                if ("id" not in item or "position" not in item or "size" not in item or
                        item["id"] == "" or item["position"] == "" or item["size"] == ""):
                    return JsonResponse({"error": "Wszystkie pola widgetu muszą być wypełnione."}, status=400)

                # Jeśli widget ma pozycję > 0, sprawdzamy unikalność
                if item["position"] > 0:
                    if item["position"] in positions_set:
                        return JsonResponse({"error": "Dla widgetów o pozycji > 0 nie mogą występować duplikaty."},
                                            status=400)
                    positions_set.add(item["position"])

            user = request.user
            for item in order_list:
                # Pobieramy lub tworzymy wpis dla danego widgetu
                widget, created = Widget.objects.get_or_create(user=user, widget_id=item["id"])
                widget.position = item["position"]
                widget.size = item["size"]
                widget.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Metoda niedozwolona"}, status=405)


@login_required
def get_widget_settings(request):
    widgets = Widget.objects.filter(user=request.user)
    widget_list = [
        {
            "id": w.widget_id,
            "position": w.position,
            "size": w.size,
        }
        for w in widgets
    ]
    return JsonResponse({"widgets": widget_list})
