from django.shortcuts import render

from .models import Pomysl


def index(request):
    context = {
        'pomysly': Pomysl.objects.all()
    }

    return render(request, 'apsi_app/index.html', context)


def login(request):
    return render(request, 'apsi_app/login.html')


def profile(request):
    context = {
        'user': request.user
    }

    return render(request, 'apsi_app/profile.html', context)


def dodaj_pomysl(request):
    return render(request, 'apsi_app/dodaj-pomysl.html')
