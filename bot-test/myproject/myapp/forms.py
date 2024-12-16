import magic
from PIL import Image
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Group
from .models import UserProfile


class FileUploadForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        uploaded_file = self.cleaned_data['file']
        file_type = magic.Magic(mime=True).from_buffer(uploaded_file.read(1024))  # Sprawdzenie MIME typu
        uploaded_file.seek(0)  # Reset wskaźnika po odczycie

        print(f"Detected MIME type: {file_type}")  # Sprawdzenie wyniku

        allowed_mime_types = ['text/plain', 'application/pdf',
                              'application/vnd.openxmlformats-officedocument.wordprocessingml.document']

        if file_type not in allowed_mime_types:
            raise ValidationError("Niedozwolony typ pliku. Obsługiwane formaty to: .txt, .pdf, .docx")

        allowed_extensions = ['.txt', '.pdf', '.docx']
        if not any(uploaded_file.name.endswith(ext) for ext in allowed_extensions):
            raise ValidationError("Nieprawidłowe rozszerzenie pliku. Obsługiwane formaty to: .txt, .pdf, .docx")

        return uploaded_file


class SearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=False, label='Search Files')


class BasicRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'group_images']
        labels = {
            'name': 'Nazwa grupy',
            'group_images': 'Obraz grupy',
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'profile_image']


def clean_profile_image(self):
    image = self.cleaned_data.get('profile_image')

    if image:
        # Walidacja rozmiaru obrazu
        img = Image.open(image)
        if img.size != (256, 256):
            raise forms.ValidationError("Obraz musi mieć wymiary 256x256 pikseli.")
    return image


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

