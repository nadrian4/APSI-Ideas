from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from .models import Ocena, Pomysl


def index(request):
    if request.method == 'POST':
        ocena_pomyslu = request.POST['ocena']
        pomysl = Pomysl.objects.get(pk=request.POST['pomysl'])
        ocena = Ocena(ocena=ocena_pomyslu, pomysl=pomysl, uzytkownik=request.user)
        ocena.save()
        
        oceny = Ocena.objects.filter(pomysl=pomysl)
        srednia_ocen = 0

        for o in oceny:
            srednia_ocen += o.ocena

        srednia_ocen = srednia_ocen / len(oceny)
        pomysl.srednia_ocen = srednia_ocen * 20
        pomysl.save()

    paginator = Paginator(Pomysl.objects.all(), 5)
    page = request.GET.get('page')
    pomysly = paginator.get_page(page)

    context = {
        'pomysly': pomysly,
        'pomysly_liczba': range(1, paginator.num_pages+1),
        'page': page
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
