from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def homepage_redirect(request):
    return render(request, 'account/login.html')


@login_required
def show_profile(request):
    return render(request, 'account/drive.html')
