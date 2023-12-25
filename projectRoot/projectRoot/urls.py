"""projectRoot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('profile/', user_views.show_profile, name='profile'),
    path('settings/', user_views.profile, name='settings'),

    path('', user_views.homepage_redirect),
    path('update/', user_views.homepage_redirect),

    path('add_folder/', user_views.create_folder, name='add_folder'),
    path('add_folder_redirect/', user_views.create_folder_call, name='add_folder_redirect'),

    path('upload_file/', user_views.upload_file, name='upload_file'),
    # path('folders/', user_views.select_folder, name='select_folder'),
    # path('folders/<user>/<folder_id>/<folder_name>/', user_views.upload_file, name='upload'),

    path('files/', user_views.list_files, name='download_file'),
    path('files/<user>/<file_id>/<file_name>/', user_views.download_file, name='download_from_id'),
    path('preview/<file_name>', user_views.preview, name='preview'),
    path('detection/', user_views.detection, name='detection'),

    # path('file2/', user_views.list_files, name='file2'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
