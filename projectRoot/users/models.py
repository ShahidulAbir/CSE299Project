from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_image = models.ImageField(default='default.jpg', upload_to='auth_img')
    credentials_file = models.FileField(default='default_credentials.json', upload_to='credentials')
    token_file = models.FileField(default='default_token.json', upload_to='token')

    def __str__(self):
        return f'{self.user.username} Profile'
