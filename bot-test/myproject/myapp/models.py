import os
import uuid

import unicodedata
from PIL import Image
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .utils.profile_img_generator import generate_profile_picture

SECRET_KEY = settings.SECRET_KEY_JIRA


# === WALIDACJE ===
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in [".txt", ".pdf", ".docx"]:
        raise ValidationError(f"Pliki o rozszerzeniu {ext} nie są dozwolone. Użyj .txt, .pdf lub .docx.")


def validate_image(file):
    try:
        img = Image.open(file)
        img.verify()
    except (IOError, SyntaxError):
        raise ValidationError("Przesłany plik nie jest prawidłowym obrazem.")


def resize_image(image_path, size=(256, 256)):
    try:
        img = Image.open(image_path)
        img = img.resize(size, Image.ANTIALIAS)
        img.save(image_path)
    except Exception as e:
        raise ValueError(f"Błąd przy zmianie rozmiaru obrazu: {e}")


def normalize_text(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()


# === MODELE ===


class Notification(models.Model):
    TYPE_CHOICES = [
        ('task', 'Task'),
        ('message', 'Message'),
        ('alert', 'Alert'),
        ('reminder', 'Reminder'),

    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.profile_image:
            self.profile_image = generate_profile_picture(self.first_name)
        super().save(*args, **kwargs)


class Group(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, unique=True)
    group_images = models.ImageField(upload_to='group_images/', blank=True, null=True)
    join_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    stylized_name = models.CharField(max_length=255, blank=True, null=True, unique=True)

    def __str__(self):
        return self.name


# Sygnał pre_save, aby przed zapisaniem ustawić stylizowaną nazwę
@receiver(pre_save, sender=Group)
def set_stylized_name(sender, instance, **kwargs):
    if instance.name:
        instance.stylized_name = normalize_text(instance.name)


class UploadedFile(models.Model):
    group = models.ForeignKey(Group, related_name="files", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    qdrant_id = models.CharField(max_length=255, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    mime_type = models.CharField(max_length=255)
    minio_path = models.CharField(max_length=500)


class GroupMember(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')


def encrypt_data(data):
    fernet = Fernet(SECRET_KEY.encode())
    return fernet.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data):
    fernet = Fernet(SECRET_KEY.encode())
    return fernet.decrypt(encrypted_data.encode()).decode()


class TrelloConfig(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="trello_config")
    api_key = models.CharField(max_length=255)
    token = models.CharField(max_length=255)

    def __str__(self):
        return f"Trello config for {self.group.name}"


class JiraConfig(models.Model):
    group = models.OneToOneField(Group, related_name='jira_config', on_delete=models.CASCADE)
    jira_url = models.URLField()
    jira_email = models.EmailField()
    jira_api_key_encrypted = models.TextField()

    @property
    def jira_api_key(self):
        if self.jira_api_key_encrypted:
            return decrypt_data(self.jira_api_key_encrypted)
        return None

    @jira_api_key.setter
    def jira_api_key(self, value):
        self.jira_api_key_encrypted = encrypt_data(value)

    def __str__(self):
        return f'Jira Config for {self.group.name}'


class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class ProjectPlatform(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class PlatformChannel(models.Model):
    PLATFORM_CHOICES = [
        ('', '---------'),
        ('discord', 'Discord'),
        ('telegram', 'Telegram'),
        ('slack', 'Slack'),
    ]
    channel_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=50)
    group = models.ForeignKey(Group, related_name='channels', on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)

    def __str__(self):
        return self.channel


class Reminder(models.Model):
    PLATFORM_CHOICES = [
        ('', '---------'),
        ('discord', 'Discord'),
        ('telegram', 'Telegram'),
        ('slack', 'Slack'),
    ]
    title = models.CharField(max_length=255, default="reminder")
    content = models.TextField(blank=True, null=True)
    channel = models.ForeignKey(PlatformChannel, on_delete=models.CASCADE, null=True)
    time = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(null=True)


class UserPlatformAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='platform_accounts')
    platform = models.ForeignKey(ProjectPlatform, on_delete=models.CASCADE, related_name='user_accounts')
    username = models.CharField(max_length=100)
    platform_user_id = models.CharField(max_length=100, unique=True)

    class Meta:
        unique_together = ('user', 'platform')


class Project(models.Model):
    STATUS_CHOICES = [
        ('In_progres', 'W toku'),
        ('Pending', 'Do zrobienia'),
        ('Completed', 'Zakończone'),
        ('At_risk', 'Zagrożony'),
    ]

    name = models.CharField(max_length=255)
    group = models.ForeignKey(Group, related_name='projects', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_projects")
    project_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_projects', null=True,
                                        blank=True)
    due_date = models.DateField(null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    def __str__(self):
        return self.name

class ProjectExternalKey(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="integrations")
    platform = models.ForeignKey(ProjectPlatform, on_delete=models.CASCADE)
    key = models.CharField(max_length=255, null=True, blank=True)

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Do zrobienia'),
        ('in_progress', 'W toku'),
        ('completed', 'Zakończone'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    due_date = models.DateField()
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    updated_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', null=True, blank=True)
    task_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_tasks', null=True,
                                     blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    attachments = models.ManyToManyField(UploadedFile, blank=True)

    def __str__(self):
        return self.title

    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status != 'completed'

    def is_due_today(self):
        return self.due_date == timezone.now().date() and self.status != 'completed'

class TaskIntegration(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="integrations")
    external_id = models.CharField(max_length=255, null=True, blank=True)
    external_user_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.system}: {self.external_id} ({self.task.title})"

class Event(models.Model):
    TYPE_CHOICES = [
        ('spotkanie', 'Meeting'),
        ('wydarzenie', 'Event'),
    ]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="events", null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='wydarzenie')
    is_all_day = models.BooleanField(default=False)


class Change(models.Model):
    task = models.ForeignKey(Task, related_name='changes', on_delete=models.CASCADE, blank=True,
                             null=True)
    project = models.ForeignKey(Project, related_name='changes',
                                on_delete=models.CASCADE)
    field = models.CharField(max_length=100)
    from_value = models.CharField(max_length=255, blank=True, null=True)
    to_value = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="changes", blank=True, null=True)
    date_changed = models.DateTimeField()


class Comment(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f'Comment by {self.author.profile.full_name} on {self.created_at.strftime("%d-%m-%Y %H:%M:%S")}'

    class Meta:
        ordering = ['created_at']



class Widget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="widgets")
    widget_id = models.CharField(max_length=50)
    # widgety o pozycji mniejszej niż 1 będą traktowane jako usunięte
    position = models.IntegerField(default=1)
    # Rozmiar widgetu, np. "small" lub "full"
    size = models.CharField(max_length=10, default="small")

    class Meta:
        unique_together = ('user', 'widget_id')
        ordering = ['position']

    def __str__(self):
        return f"{self.user.username} - {self.widget_id} (position: {self.position}, size: {self.size})"