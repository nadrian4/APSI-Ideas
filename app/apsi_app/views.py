from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from .models import Ocena, Glosowanie, Pomysl, GlosowaniePomysl


def index(request):
    if request.method == 'POST':
        pomysl = Pomysl.objects.get(pk=request.POST['pomysl'])

        if not Ocena.objects.filter(uzytkownik=request.user, pomysl=pomysl):
            ocena_pomyslu = request.POST['ocena']
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


def glosowania(request):
    context = {
        'glosowania': Glosowanie.objects.all()
    }

    return render(request, 'apsi_app/glosowania.html', context)


def utworz_glosowanie(request):
    pomysly = Pomysl.objects.all()

    context = {
        'pomysly': pomysly
    }

    if request.method == 'POST':
        nazwa = request.POST['nazwa']
        wybrane_pomysly_id = request.POST.getlist('pomysly')
        wybrane_pomysly = []

        for id in wybrane_pomysly_id:
            wybrane_pomysly.append(Pomysl.objects.get(pk=id))

        glosowanie = Glosowanie(nazwa=nazwa)
        glosowanie.save()

        for pomysl in wybrane_pomysly:
            glosowanie_pomysl = GlosowaniePomysl(glosowanie=glosowanie, pomysl=pomysl)
            glosowanie_pomysl.save()

        return redirect('glosowania')
    else:
        return render(request, 'apsi_app/utworz-glosowanie.html', context)


def strona_glosowania(request):
    glosowanie_id = request.GET['glosowanie_id']
    glosowanie = Glosowanie.objects.get(pk=glosowanie_id)
    glosowanie_pomysl_list = GlosowaniePomysl.objects.filter(glosowanie=glosowanie)
    pomysly = []

    for glosowanie_pomysl in glosowanie_pomysl_list:
        pomysly.append(glosowanie_pomysl.pomysl)

    context = {
        'glosowanie': glosowanie,
        'pomysly': pomysly
    }

    return render(request, 'apsi_app/strona-glosowania.html', context)