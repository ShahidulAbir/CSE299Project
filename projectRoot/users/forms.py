from django import forms
from .models import Profile, UploadedFile


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['auth_image', 'credentials_file', 'token_file']


class FolderNameForm(forms.ModelForm):
    folder_name = forms.CharField(label='Name')


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']

