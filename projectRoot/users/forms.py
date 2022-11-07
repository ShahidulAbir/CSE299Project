from django import forms
from .models import Profile


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['auth_image', 'credentials_file', 'token_file']


class FolderNameForm(forms.ModelForm):
    folder_name = forms.CharField(label='Name')
