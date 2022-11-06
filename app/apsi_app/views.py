from django.shortcuts import render, redirect

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
    if request.method == 'POST':
        tytul = request.POST['tytul']
        tresc = request.POST['tresc']

        pomysl = Pomysl(tytul=tytul, tresc=tresc, uzytkownik=request.user)
        pomysl.save()
        return redirect('index')
    else:
        return render(request, 'apsi_app/dodaj-pomysl.html')
