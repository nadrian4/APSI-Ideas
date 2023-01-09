from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import transaction

from .models import Konkurs, Glosowanie, Pomysl, GlosowaniePomysl, Glos, Ocena, Komentarz
from .models import KATEGORIE, ROLE
from .forms import PomyslForm

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
    pomysly_kto_moze_oceniac = []

    user_groups = request.user.groups.all()

    for pomysl in pomysly:
        moze_oceniac = False

        if user_groups[0].__str__() == pomysl.kto_moze_oceniac or pomysl.kto_moze_oceniac == 'Wszyscy':
            moze_oceniac = True

        pomysly_kto_moze_oceniac.append({'pomysl': pomysl, 'moze_oceniac': moze_oceniac})

    context = {
        'pomysly': pomysly,
        'pomysly_kto_moze_oceniac': pomysly_kto_moze_oceniac,
        'pomysly_liczba': range(1, paginator.num_pages+1),
        'page': page
    }

    return render(request, 'apsi_app/index.html', context)


def konkursy(request):
    paginator = Paginator(Konkurs.objects.all(), 5)
    page = request.GET.get('page')
    konkursy = paginator.get_page(page)

    context = {
        'konkursy': konkursy,
        'page': page
    }

    if request.user.groups.filter(name='Członek komisji'):
        return render(request, 'apsi_app/konkursy/konkursy.html', context)
    else:
        return render(request, 'apsi_app/odmowa-dostepu.html', {'uprawnione_grupy': 'Członek komisji'})


def strona_konkursu(request):
    konkurs = Konkurs.objects.get(pk=request.GET['konkurs_id'])
    pomysly_uzytkownika = Pomysl.objects.filter(uzytkownik=request.user)

    if request.method == 'POST':
        wybrane_pomysly_id = request.POST.getlist('pomysly')
        wybrane_pomysly = Pomysl.objects.filter(pk__in=wybrane_pomysly_id)

        with transaction.atomic():
            for pomysl in wybrane_pomysly:
                pomysl.konkurs = konkurs
                pomysl.save()

        odznaczone_pomysly = [pomysl for pomysl in pomysly_uzytkownika if pomysl not in wybrane_pomysly]

        with transaction.atomic():
            for pomysl in odznaczone_pomysly:
                if pomysl.konkurs == konkurs:
                    pomysl.konkurs = None
                    pomysl.save()

    pomysly_konkursu = Pomysl.objects.filter(konkurs=konkurs)
    pomysly_uzytkownika = Pomysl.objects.filter(uzytkownik=request.user)

    context = {
        'konkurs': konkurs,
        'pomysly_konkursu': pomysly_konkursu,
        'pomysly_niedodane': [pomysl for pomysl in pomysly_uzytkownika if pomysl not in pomysly_konkursu],
        'pomysly_dodane': [pomysl for pomysl in pomysly_uzytkownika if pomysl in pomysly_konkursu],
    }

    return render(request, 'apsi_app/konkursy/strona-konkursu.html', context)


def utworz_konkurs(request):
    if request.method == 'POST':
        nazwa = request.POST['nazwa']
        data_koniec = request.POST['data_koniec']
        konkurs = Konkurs(nazwa=nazwa, data_koniec=data_koniec)
        konkurs.save()

        return redirect('konkursy')
    else:
        return render(request, 'apsi_app/konkursy/utworz-konkurs.html')


def usun_konkurs(request):
    if request.method == 'POST':
        konkurs_id = request.GET['konkurs_id']
        konkurs = Konkurs.objects.get(pk=konkurs_id)
        konkurs.delete()

        return redirect('konkursy')

    return render(request, 'apsi_app/konkursy/usun-konkurs.html')


def login(request):
    return render(request, 'apsi_app/login.html')


def profile(request):
    user = request.user
    user_groups = user.groups.all()
    
    for group in user_groups:
        print(group)

    paginator = Paginator(Pomysl.objects.filter(uzytkownik=request.user), 5)
    page = request.GET.get('page')
    pomysly_uzytkownika = paginator.get_page(page)

    context = {
        'user': request.user,
        'user_groups': user_groups,
        'pomysly_uzytkownika': pomysly_uzytkownika,
    }

    return render(request, 'apsi_app/profile.html', context)


def dodaj_pomysl(request):
    if request.method == 'POST':
        pomysl_form = PomyslForm(request.POST, request.FILES)

        if pomysl_form.is_valid():
            inst = pomysl_form.save(commit=False)
            inst.uzytkownik = request.user
            inst.save()

            # tytul = pomysl_form.cleaned_data['tytul']
            # tresc = pomysl_form.cleaned_data['tresc']
            # kategoria = pomysl_form.cleaned_data['kategoria']
            # kto_moze_oceniac = pomysl_form.cleaned_data['kto_moze_oceniac']
            # plik = pomysl_form.cleaned_data['plik']

            # pomysl = Pomysl(tytul=tytul, tresc=tresc, kategoria=kategoria, kto_moze_oceniac=kto_moze_oceniac, uzytkownik=request.user)
            # pomysl.save()

            return redirect('index')
        else:
            print('form invalid')
    else:
        pomysl_form = PomyslForm()

    context = {
        'pomysl_form': pomysl_form,
        'kategorie': [k[1] for k in KATEGORIE],
        'role': [r[1] for r in ROLE],
    }

    return render(request, 'apsi_app/dodaj-pomysl.html', context)

    # if request.method == 'POST':
    #     tytul = request.POST['tytul']
    #     tresc = request.POST['tresc']
    #     kategoria = request.POST['kategoria']
    #     kto_moze_oceniac = request.POST['kto_moze_oceniac']

    #     pomysl = Pomysl(tytul=tytul, kategoria=kategoria, kto_moze_oceniac=kto_moze_oceniac, tresc=tresc, uzytkownik=request.user)
    #     pomysl.save()
    #     return redirect('index')
    # else:
    #     kategorie = ['Edukacja', 'Życie społeczne', 'Infrastruktura']
    #     kto_moze_oceniac = ['Student', 'Pracownik', 'Wszyscy']

    #     context = {
    #         'kategorie': kategorie,
    #         'kto_moze_oceniac': kto_moze_oceniac
    #     }

    #     return render(request, 'apsi_app/dodaj-pomysl.html', context)


def usun_pomysl(request):
    if request.method == 'POST':
        pomysl_id = request.GET['pomysl_id']
        pomysl = Pomysl.objects.get(pk=pomysl_id)
        pomysl.delete()

        return redirect('profile')

    return render(request, 'apsi_app/usun-pomysl.html')


def glosowania(request):
    paginator = Paginator(Glosowanie.objects.all().order_by('data_koniec'), 5)
    page = request.GET.get('page')
    glosowania = paginator.get_page(page)

    context = {
        'glosowania': glosowania,
        'page': page
    }

    return render(request, 'apsi_app/glosowania/glosowania.html', context)


def utworz_glosowanie(request):
    if request.method == 'POST':
        if 'wybierz_konkurs' in request.POST:
            wybrany_konkurs = Konkurs.objects.get(pk=request.POST['wybierz_konkurs'])

            context = {
                'pomysly': Pomysl.objects.filter(konkurs=wybrany_konkurs),
                'konkursy': Konkurs.objects.all(),
                'wybrany_konkurs': wybrany_konkurs
            }

            return render(request, 'apsi_app/glosowania/utworz-glosowanie.html', context)
        elif 'utworz_glosowanie' in request.POST:
            nazwa = request.POST['nazwa']
            max_glos = request.POST['max_glos']
            data_koniec = request.POST['data_koniec']
            wybrane_pomysly_id = request.POST.getlist('pomysly')
            wybrane_pomysly = []

            for id in wybrane_pomysly_id:
                wybrane_pomysly.append(Pomysl.objects.get(pk=id))

            glosowanie = Glosowanie(nazwa=nazwa, max_glos=max_glos, data_koniec=data_koniec)

            with transaction.atomic():
                glosowanie.save()

                for pomysl in wybrane_pomysly:
                    glosowanie_pomysl = GlosowaniePomysl(glosowanie=glosowanie, pomysl=pomysl, srednia_glosow=0)
                    glosowanie_pomysl.save()

            return redirect('glosowania')
    else:
        context = {
            'konkursy': Konkurs.objects.all()
        }

        return render(request, 'apsi_app/glosowania/utworz-glosowanie.html', context)


def strona_glosowania(request):
    if request.method == 'POST':
        glosowanie = Glosowanie.objects.get(pk=request.POST['glosowanie_id'])
        pomysl = Pomysl.objects.get(pk=request.POST['pomysl_id'])
        uzytkownik = request.user

        if not Glos.objects.filter(glosowanie=glosowanie, pomysl=pomysl, uzytkownik=uzytkownik):
            glos = Glos(glosowanie=glosowanie, pomysl=pomysl, uzytkownik=uzytkownik, glos=request.POST['glos'])
            glos.save()

        else:
            glos = Glos.objects.get(glosowanie=glosowanie, pomysl=pomysl, uzytkownik=uzytkownik)
            glos.glos = request.POST['glos']
            glos.save()
    
        glosy_pomysl = Glos.objects.filter(glosowanie=glosowanie, pomysl=pomysl)
        glosy_pomysl = [g.glos for g in glosy_pomysl]
        glosy_pomysl_mean = sum(glosy_pomysl) / len(glosy_pomysl)

        glosowanie_pomysl = GlosowaniePomysl.objects.get(glosowanie=glosowanie, pomysl=pomysl)
        glosowanie_pomysl.srednia_glosow = glosy_pomysl_mean
        glosowanie_pomysl.save()

    glosowanie_id = request.GET['glosowanie_id']
    glosowanie = Glosowanie.objects.get(pk=glosowanie_id)
    glosowanie_pomysl_list = GlosowaniePomysl.objects.filter(glosowanie=glosowanie)
    pomysly_srednia_glos = []
    
    for glosowanie_pomysl in glosowanie_pomysl_list:
        pomysly_srednia_glos.append({'pomysl': glosowanie_pomysl.pomysl, 'glos': glosowanie_pomysl.srednia_glosow})

    glos_list = list(range(1, glosowanie.max_glos + 1))

    context = {
        'glosowanie': glosowanie,
        'glosowanie_id': glosowanie_id,
        'pomysly_srednia_glos': pomysly_srednia_glos,
        'glos_list': glos_list
    }

    return render(request, 'apsi_app/glosowania/strona-glosowania.html', context)


def usun_glosowanie(request):
    if request.method == 'POST':
        glosowanie_id = request.GET['glosowanie_id']
        glosowanie = Glosowanie.objects.get(pk=glosowanie_id)
        glosowanie.delete()

        return redirect('glosowania')

    return render(request, 'apsi_app/glosowania/usun-glosowanie.html')


def komentarze(request):
    pomysl_id = request.GET['pomysl_id']
    pomysl = Pomysl.objects.get(pk=pomysl_id)
    komentarze = Komentarz.objects.filter(pomysl=pomysl_id).order_by('-rodzic');
    
    context = {
        'komentarze': komentarze,
        'pomysl': pomysl,
        'pomysl_id': pomysl_id,
    }

    return render(request, 'apsi_app/komentarze.html', context)


def dodaj_komentarz(request):
    pomysl_id = request.GET.get('pomysl_id', None)
    komentarz_id = request.GET.get('komentarz_id', None)
    
    if komentarz_id:
        komentarz = Komentarz.objects.get(pk=komentarz_id)
        pomysl_id = komentarz.pomysl.pk
        komentarz_do_komentarza = True
    else:
        komentarz = None
        komentarz_do_komentarza = False

    pomysl = Pomysl.objects.get(pk=pomysl_id)

    if request.method == 'POST':
        tresc = request.POST['tresc']
        komentarz = Komentarz(tresc=tresc, uzytkownik=request.user, rodzic=komentarz, pomysl=pomysl)
        komentarz.save()
        return redirect(reverse('komentarze')+f"?pomysl_id={pomysl_id}")

    context = {
        'komentarz_id': komentarz_id,
        'komentarz': komentarz,
        'pomysl_id': pomysl_id,
        'pomysl': pomysl,
        'komentarz_do_komentarza': komentarz_do_komentarza,
    }
    
    return render(request, 'apsi_app/dodaj-komentarz.html', context)

