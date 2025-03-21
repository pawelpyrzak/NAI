from datetime import datetime

import magic
from PIL import Image
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Group, Event, Project, Task, JiraConfig, PlatformChannel, GroupMember, UserPlatformAccount, \
    Platform, ProjectPlatform, TrelloConfig
from .models import UserProfile


class FileUploadForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        uploaded_file = self.cleaned_data['file']
        # Odczytaj pierwsze 1024 bajty do wykrycia MIME type
        file_type = magic.Magic(mime=True).from_buffer(uploaded_file.read(1024))
        uploaded_file.seek(0)  # Reset wskaźnika po odczycie

        print(f"Detected MIME type: {file_type}")

        # Rozszerzona lista dozwolonych MIME types
        allowed_mime_types = [
            'text/plain',
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # DOCX
            'application/msword',  # DOC
            'application/zip',
            'image/jpeg',
            'image/png',
            'image/gif',
            'application/vnd.ms-excel',  # Excel (xls)
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # Excel (xlsx)
        ]

        if file_type not in allowed_mime_types:
            raise ValidationError(
                "Niedozwolony typ pliku. Obsługiwane formaty to: .txt, .pdf, .docx, .doc, "
                ".jpeg, .jpg, .png, .gif, .xls, .xlsx"
            )

        # Rozszerzona lista dozwolonych rozszerzeń
        allowed_extensions = [
            '.txt',
            '.pdf',
            '.docx',
            '.doc',
            '.jpeg',
            '.jpg',
            '.png',
            '.gif',
            '.xls',
            '.xlsx',
        ]
        if not any(uploaded_file.name.lower().endswith(ext) for ext in allowed_extensions):
            raise ValidationError(
                "Nieprawidłowe rozszerzenie pliku. Obsługiwane formaty to: .txt, .pdf, .docx, .doc, .zip, "
                ".jpeg, .jpg, .png, .gif, .xls, .xlsx"
            )

        return uploaded_file


class SearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=False, label='Search Files')


class BasicRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'profile_image']


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'group_images']
        labels = {
            'name': 'Nazwa grupy',
            'group_images': 'Obraz grupy',
        }


class JiraConfigForm(forms.ModelForm):
    jira_api_key = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        required=False,
        label="Klucz API"
    )

    class Meta:
        model = JiraConfig
        fields = ['jira_url', 'jira_email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.jira_api_key:
            self.fields['jira_api_key'].initial = self.instance.jira_api_key
class TrelloConfigForm(forms.ModelForm):
    class Meta:
        model = TrelloConfig
        exclude = ['group']  # Exclude the 'group' field

    api_key = forms.CharField(widget=forms.PasswordInput())
    token = forms.CharField(widget=forms.PasswordInput())
# Formularz dla Projektu

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description','status','due_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwa projektu'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Opis projektu'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [('', '---------')] + list(self.fields['status'].choices)
        for field in self.fields.values():
            field.required = False


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'start_date', 'due_date', 'assignee','priority', 'project']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            user_groups = GroupMember.objects.filter(user=user).values_list('group', flat=True)
            self.fields['project'].queryset = Project.objects.filter(group__in=user_groups)

class TaskEditForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'start_date', 'due_date', 'assignee',
                  'priority']  # Usunięto pole 'project'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

        # # Usuń pole 'project', jeśli istnieje
        # if 'project' in self.fields:
        #     del self.fields['project']
        #
        # # Filtrowanie użytkowników na podstawie grupy projektu
        # if 'project' in self.initial:
        #     project = self.initial['project']
        # elif self.instance and hasattr(self.instance, 'project') and self.instance.project:
        #     project = self.instance.project
        # else:
        #     project = None

        if project and project.group:
            self.fields['assignee'].queryset = User.objects.filter(
                id__in=GroupMember.objects.filter(group=project.group).values_list('user', flat=True)
            )
        self.fields['assignee'].label_from_instance = lambda obj: obj.profile.full_name if obj.profile.full_name else obj.username

        self.fields['status'].choices = [('', '---------')] + list(self.fields['status'].choices)
        self.fields['priority'].choices = [('', '---------')] + list(self.fields['priority'].choices)



def clean_profile_image(self):
    image = self.cleaned_data.get('profile_image')

    if image:
        img = Image.open(image)
        if img.size != (256, 256):
            raise forms.ValidationError("Obraz musi mieć wymiary 256x256 pikseli.")
    return image


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'start_date', "end_date"]

    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=datetime.now().date()
    )

    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=datetime.now().date()
    )

    def clean_event_date(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if end_date and end_date < datetime.now():
            raise forms.ValidationError("Data zakończenia wydarzenia nie może być w przeszłości.")

        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError("Data zakończenia musi być późniejsza niż data rozpoczęcia.")


class PlatformChannelForm(forms.ModelForm):
    class Meta:
        model = PlatformChannel
        fields = ['channel_id', 'name', 'platform']
        widgets = {
            'channel_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter channel ID'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter channel name'}),
            'platform': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select platform'}),

        }
        labels = {
            'channel_id': 'Channel ID',
            'name': 'Channel Name',
            'platform': 'Platform',
        }
