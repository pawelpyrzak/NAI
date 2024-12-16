import json

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import serializers, viewsets

from .decorators import user_belongs_to_group
from .forms import BasicRegistrationForm, ProfileUpdateForm, GroupForm
from .forms import FileUploadForm
from .forms import SearchForm
from .models import Group, UploadedFile
from .models import GroupMember, Task
from .utils.qdrant import get_file_from_qdrant, search_files_in_group, process_and_store_file, get_all_files, \
    file_delete
from .utils.site_bot import get_bot_response


# User authentication views
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Zalogowano pomyślnie!")
            return redirect('home')  # Redirect to homepage
        else:
            messages.error(request, "Błędne dane logowania. Spróbuj ponownie.")
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        form = BasicRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session['user_id'] = user.id  # Store user ID in session
            return redirect('register_step2')
    else:
        form = BasicRegistrationForm()
    return render(request, 'register/register_step1.html', {'form': form})


def register_step2(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            del request.session['user_id']  # Remove session data
            login(request, user)  # Automatically log in the user
            return redirect('home')
    else:
        form = ProfileUpdateForm()
    return render(request, 'register/register_step2.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


# Group views
@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save()  # Save the group
            GroupMember.objects.create(user=request.user, group=group, role='admin')  # Add creator as admin
            return redirect('teamPage', group_id=group.id)  # Redirect to group details
    else:
        form = GroupForm()
    return render(request, 'teamCreate.html', {'form': form})

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
    return render(request, 'teamJoin.html')

@login_required
@user_belongs_to_group
def team_page(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    return render(request, 'teamPage.html', {'group': group})


@login_required
def teams(request):
    groups = GroupMember.objects.filter(user=request.user).select_related('group')
    return render(request, 'groups.html', {'groups': groups})


class GroupInfoView(TemplateView):
    template_name = 'group_info.html'

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


# File management views
@login_required
@user_belongs_to_group
def upload_file(request, group_id):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            try:
                qdrant_id = process_and_store_file(file, group_id)
                UploadedFile.objects.create(
                    group_id=group_id,
                    name=file.name,
                    qdrant_id=qdrant_id,
                )
                return redirect('search_files', group_id=group_id)
            except ValueError as e:
                form.add_error('file', str(e))
    else:
        form = FileUploadForm()

    return render(request, "upload_file.html", {"form": form})


@login_required
def delete_file(request, group_id, file_uuid):
    # Pobranie zespołu i pliku
    group = get_object_or_404(Group, id=group_id)
    file = get_object_or_404(UploadedFile, qdrant_id=file_uuid, group=group)

    # Sprawdzamy, czy użytkownik jest członkiem grupy i ma rolę 'admin'
    group_member = get_object_or_404(GroupMember, user=request.user, group=group)

    if group_member.role == 'admin':
        # Usuwamy plik z bazy danych
        file_delete(file.qdrant_id)  # Usuwanie z Qdrant (zakładając, że masz funkcję file_delete)
        file.delete()  # Usuwanie pliku z bazy danych

        # Wyświetlamy komunikat o sukcesie
        messages.success(request, 'Plik został pomyślnie usunięty.')
        return redirect('search_files', group_id=group.id)
    else:
        # Wyświetlamy komunikat o braku uprawnień
        messages.error(request, 'Nie masz uprawnień do usuwania tego pliku.')
        return redirect('search_files', group_id=group.id)

@login_required
def download_file(request, qdrant_id):
    try:
        file_data = get_file_from_qdrant(qdrant_id)
        print(file_data['file_binary'])
        response = HttpResponse(file_data['file_binary'], content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_data["file_name"]}"'
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
            results = search_files_in_group(query, group.id)
            all_files = False
    else:
        form = SearchForm()
        results = get_all_files(group_id)
    get_all_files(group_id)
    return render(request, "search_files.html",
                  {"form": form, "results": results, "group": group, "all_files": all_files,"group_member": group_member})


# Task views
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


@login_required
def tasks(request):
    return render(request, 'Tasks.html')


# Bot communication view
@login_required
def chat_with_bot(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON from the request
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "Message is required."}, status=400)

            # Get bot response
            bot_response = get_bot_response(user_message)

            return JsonResponse({"response": bot_response})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=400)


# Miscellaneous views
@login_required
def homepage(request):
    context = {'csrf_token': get_token(request)}  # Add CSRF token to the context
    return render(request, 'home.html', context)


def home(request):
    return render(request, 'main.html')


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def calendar(request):
    return render(request, 'calendar.html')
