from django.db import models
from django.contrib.auth.models import User
from mimetypes import guess_type
from cryptography.fernet import Fernet


def generate_key():
    key = Fernet.generate_key()
    string_key = key.decode("utf-8")

    return string_key


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_image = models.ImageField(default='default_auth_image.jpg', upload_to='auth_img')
    credentials_file = models.FileField(default='credentials/default_credentials.json', upload_to='credentials')
    token_file = models.FileField(default='token/default_token.json', upload_to='token')
    secret_key = models.CharField(default=generate_key, max_length=100)
    rootFolder = models.CharField(default="", max_length=100)

    def __str__(self):
        return f'{self.user.username} Profile'


class UploadedFile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(default=None, upload_to='uploadedFile')
    mimetype = ""
    id = ""

    def __str__(self):
        return self.file.name
