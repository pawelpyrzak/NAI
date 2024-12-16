import os
import uuid

from PIL import Image
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from .utils.profile_img_generator import generate_profile_picture


# === WALIDACJE ===
def validate_file_extension(value):
    """Walidator rozszerzenia pliku."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in [".txt", ".pdf", ".docx"]:
        raise ValidationError(f"Pliki o rozszerzeniu {ext} nie są dozwolone. Użyj .txt, .pdf lub .docx.")


def validate_image(file):
    try:
        img = Image.open(file)
        img.verify()  # Weryfikacja zawartości obrazu
    except (IOError, SyntaxError):
        raise ValidationError("Przesłany plik nie jest prawidłowym obrazem.")


def resize_image(image_path, size=(256, 256)):
    try:
        img = Image.open(image_path)
        img = img.resize(size, Image.ANTIALIAS)
        img.save(image_path)
    except Exception as e:
        raise ValueError(f"Błąd przy zmianie rozmiaru obrazu: {e}")


# === MODELE ===
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.profile_image:
            self.profile_image = generate_profile_picture(self.user.username)
        super().save(*args, **kwargs)


class Reminders(models.Model):
    PLATFORM_CHOICES = [
        ('discord', 'Discord'),
        ('telegram', 'Telegram'),
        ('slack', 'Slack'),
    ]
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    time = models.DateTimeField()
    sent_at = models.DateTimeField()
    user_id = models.CharField(max_length=255)

    class Meta:
        db_table = 'reminder'


class Group(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255)
    group_images = models.ImageField(upload_to='group_images/', blank=True, null=True)
    join_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class UploadedFile(models.Model):
    group = models.ForeignKey(Group, related_name="files", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    qdrant_id = models.CharField(max_length=255, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


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

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


class Project(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_projects")


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    due_date = models.DateField()
    assignee = models.CharField(max_length=255, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    updated_at = models.DateTimeField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks", null=True)

    class Meta:
        db_table = 'tasks'

    def __str__(self):
        return self.title


class Event(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="events")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")


class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
