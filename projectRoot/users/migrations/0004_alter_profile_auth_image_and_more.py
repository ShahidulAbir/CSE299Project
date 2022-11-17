# Generated by Django 4.1.2 on 2022-11-09 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_profile_auth_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='auth_image',
            field=models.ImageField(default='default_auth_image.jpg', upload_to='auth_img'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='credentials_file',
            field=models.FileField(default='default_credentials.json', upload_to='credentials'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='token_file',
            field=models.FileField(default='default_token.json', upload_to='token'),
        ),
    ]
