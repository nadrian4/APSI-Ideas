from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout

from .models import Konkurs, Glosowanie, Pomysl, GlosowaniePomysl, Glos, Ocena, Komentarz, SlowoKluczowe, PomyslSlowoKluczowe, Watek, ForumPost
from .forms import PomyslForm
from .models import KATEGORIE, ROLE
from .forms import PomyslForm, WatekForm
from .models import Konkurs, Glosowanie, Pomysl, GlosowaniePomysl, Glos, Ocena, Komentarz, SlowoKluczowe, \
    PomyslSlowoKluczowe, CzlonekKomisji


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

        if user_groups:
            if user_groups[0].__str__() == pomysl.kto_moze_oceniac or pomysl.kto_moze_oceniac == 'Wszyscy':
                moze_oceniac = True

        pomysl_slowa_kluczowe = PomyslSlowoKluczowe.objects.filter(pomysl=pomysl)
        pomysly_kto_moze_oceniac.append({
            'pomysl': pomysl,
            'moze_oceniac': moze_oceniac,
            'slowa_kluczowe': [x.slowo_kluczowe.nazwa for x in pomysl_slowa_kluczowe]
        })

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

    if request.user.groups.filter(name='Członek komisji') or request.user.groups.filter(name='Organizator'):
        return render(request, 'apsi_app/konkursy/konkursy.html', context)
    else:
        return render(request, 'apsi_app/odmowa-dostepu.html', {'uprawnione_grupy': 'Członek komisji, Organizator'})


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


def sklad_komisji(request):
    konkurs = Konkurs.objects.get(pk=request.GET['konkurs_id'])
    sklad_komisji = CzlonekKomisji.objects.filter(konkurs=konkurs)
    if request.method == 'POST':
        if 'dodaj_czlonka' in request.POST and 'wyborNowegoCzlonka' in request.POST:
            username = request.POST['wyborNowegoCzlonka']
            user = User.objects.filter(username=username)
            if len(user) == 1 and user[0].id not in [u.uzytkownik.id for u in sklad_komisji]:
                nowy_czlonek = CzlonekKomisji(uzytkownik_id=user[0].id, konkurs_id=konkurs.id)
                nowy_czlonek.save()
                sklad_komisji = CzlonekKomisji.objects.filter(konkurs=konkurs)
        elif 'usunCzlonka' in request.POST:
            id_czlonka = request.POST['usunCzlonka']
            czlonek_komisji = CzlonekKomisji.objects.get(pk=id_czlonka)
            czlonek_komisji.delete()
            sklad_komisji = CzlonekKomisji.objects.filter(konkurs=konkurs)
    reszta = User.objects.exclude(pk__in=[i.uzytkownik_id for i in sklad_komisji])

    context = {
        'konkurs': konkurs,
        'sklad_komisji': [c for c in sklad_komisji],
        'reszta': reszta
    }
    if request.user.groups.filter(name='Organizator'):
        return render(request, 'apsi_app/konkursy/sklad-komisji.html', context)
    else:
        return render(request, 'apsi_app/odmowa-dostepu.html', {'uprawnione_grupy': 'Organizator'})


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


def profile(request):
    if request.user.is_anonymous:
        return redirect('login')

    if request.method == 'POST':
        if 'wyloguj_sie' in request.POST:
            logout(request)
            return redirect('login')

    user = request.user
    user_groups = user.groups.all()

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
        print(request.POST['slowakluczowe'].split(', '))

        if pomysl_form.is_valid():
            with transaction.atomic():
                pomysl = pomysl_form.save(commit=False)
                pomysl.uzytkownik = request.user
                pomysl.save()

                for slowo_kluczowe in request.POST['slowakluczowe'].split(', '):
                    slowo_kluczowe_model = SlowoKluczowe(nazwa=slowo_kluczowe)
                    slowo_kluczowe_model.save()
                    pomysl_slowo_kluczowe = PomyslSlowoKluczowe(pomysl=pomysl, slowo_kluczowe=slowo_kluczowe_model)
                    pomysl_slowo_kluczowe.save()

            return redirect('index')
        else:
            print('form invalid')
            print(pomysl_form.errors)

    pomysl_form = PomyslForm()

    context = {
        'pomysl_form': pomysl_form,
        'kategorie': [k[1] for k in KATEGORIE],
        'role': [r[1] for r in ROLE],
    }

    return render(request, 'apsi_app/dodaj-pomysl.html', context)


def usun_pomysl(request):
    if request.method == 'POST':
        pomysl_id = request.GET['pomysl_id']
        pomysl = Pomysl.objects.get(pk=pomysl_id)
        pomysl.delete()

        return redirect('profile')

    return render(request, 'apsi_app/usun-pomysl.html')


def edytuj_pomysl(request):
    pomysl = Pomysl.objects.get(pk=request.GET['pomysl_id'])

    if request.method == 'POST':
        pomysl.tytul = request.POST['tytul']
        pomysl.tresc = request.POST['tresc']
        pomysl.planowane_korzysci = request.POST['planowane_korzysci']
        pomysl.planowane_koszty = request.POST['planowane_koszty']
        pomysl.kategoria = request.POST['kategoria']
        pomysl.kto_moze_oceniac = request.POST['kto_moze_oceniac']
        pomysl.save()
        return redirect('profile')

    context = {
        'pomysl': pomysl,
        'kategorie': [k[1] for k in KATEGORIE],
        'role': [r[1] for r in ROLE],
    }

    return render(request, 'apsi_app/edytuj-pomysl.html', context)


def edytuj_stan_pomyslu(request):
    pomysl_id = request.POST['pomysl_id']
    pomysl = Pomysl.objects.get(pk=pomysl_id)

    if request.method == 'POST':
        pomysl.stan = request.POST['stan']
        pomysl.wiadomosc = request.POST['wiadomosc']
        pomysl.save()
        return redirect('profile')

    context = {
        'pomysl': pomysl,
        'kategorie': [k[1] for k in KATEGORIE],
        'role': [r[1] for r in ROLE],
    }

    #return redirect('edytuj-pomysl', pomysl_id=pomysl.pk)

    #return render(request, 'apsi_app/edytuj-stan-pomyslu.html', context)


def glosowania(request):
    paginator = Paginator(Glosowanie.objects.all().order_by('data_koniec'), 5)
    page = request.GET.get('page')
    glosowania = paginator.get_page(page)

    context = {
        'glosowania': glosowania,
        'page': page
    }

    if request.user.groups.filter(name='Członek komisji'):
        return render(request, 'apsi_app/glosowania/glosowania.html', context)
    else:
        return render(request, 'apsi_app/odmowa-dostepu.html', {'uprawnione_grupy': 'Członek komisji'})


def utworz_glosowanie(request):
    if request.method == 'POST':
        if 'wybierz_konkurs' in request.POST:
            wybrany_konkurs = Konkurs.objects.get(pk=request.POST['wybierz_konkurs'])
            pomysly = Pomysl.objects.filter(konkurs=wybrany_konkurs)
            pomysly_oceny = [{'pomysl': pomysl, 'liczba_ocen': len(Ocena.objects.filter(pomysl=pomysl))} for pomysl in pomysly]

            context = {
                'pomysly_oceny': pomysly_oceny,
                'konkursy': Konkurs.objects.all(),
                'wybrany_konkurs': wybrany_konkurs
            }

            return render(request, 'apsi_app/glosowania/utworz-glosowanie.html', context)
        elif 'utworz_glosowanie' in request.POST:
            nazwa = request.POST['nazwa']
            data_koniec = request.POST['data_koniec']
            wybrane_pomysly_id = request.POST.getlist('pomysly')
            wybrane_pomysly = []

            for id in wybrane_pomysly_id:
                wybrane_pomysly.append(Pomysl.objects.get(pk=id))

            max_glos = len(wybrane_pomysly)
            glosowanie = Glosowanie(nazwa=nazwa, max_glos=max_glos, data_koniec=data_koniec)

            with transaction.atomic():
                if max_glos != 0:
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
        if 'wyczysc_glosy' in request.POST:
            glosowanie = Glosowanie.objects.get(pk=request.GET['glosowanie_id'])
            uzytkownik = request.user
            glosy_pomysl = Glos.objects.filter(glosowanie=glosowanie, uzytkownik=uzytkownik)
            glosy_pomysl.delete()
        else:
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

            glosy_pomysl = Glos.objects.filter(glosowanie=glosowanie, pomysl=pomysl, uzytkownik=uzytkownik)
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

    glosowanie = Glosowanie.objects.get(pk=request.GET['glosowanie_id'])
    uzytkownik = request.user
    glosy = Glos.objects.filter(glosowanie=glosowanie, uzytkownik=uzytkownik)
    glosy = [g.glos for g in glosy]
    glos_list = []
    for i in range(1, glosowanie.max_glos + 1):
        if i not in glosy:
            glos_list.append(i)

    glosy = Glos.objects.filter(glosowanie=glosowanie, uzytkownik=uzytkownik)
    context = {
        'glosowanie': glosowanie,
        'glosowanie_id': glosowanie_id,
        'pomysly_srednia_glos': pomysly_srednia_glos,
        'glos_list': glos_list,
        'glosy': glosy
    }

    return render(request, 'apsi_app/glosowania/strona-glosowania.html', context)


def usun_glosowanie(request):
    if request.method == 'POST':
        glosowanie_id = request.GET['glosowanie_id']
        glosowanie = Glosowanie.objects.get(pk=glosowanie_id)
        glosowanie.delete()

        return redirect('glosowania')

    return render(request, 'apsi_app/glosowania/usun-glosowanie.html')

def wyczysc_glosy(request):
    if request.method == 'POST':
        glosowanie_id = request.GET['glosowanie_id']
        glosowanie = Glosowanie.objects.get(pk=glosowanie_id)
        glosowanie.delete()

        return redirect('glosowania')

    return render(request, 'apsi_app/glosowania/usun-glosowanie.html')


def komentarze(request):
    pomysl_id = request.GET['pomysl_id']
    pomysl = Pomysl.objects.get(pk=pomysl_id)
    komentarzeDoPomyslu = Komentarz.objects.filter(pomysl=pomysl_id,rodzic=None)
    
    komentarzeGlebokosc = []
    for k in komentarzeDoPomyslu:
        _r = k.get_children_with_depths()
        if 0 < len(_r):
            komentarzeGlebokosc.extend(_r)

    context = {
        'komentarzeGlebokosc': komentarzeGlebokosc,
        'pomysl': pomysl,
        'kategorie': [k[1] for k in KATEGORIE],
        'role': [r[1] for r in ROLE],
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


def forum(request):
    paginator = Paginator(Watek.objects.all().order_by('-id'), 10)
    page = request.GET.get('page')
    watki = paginator.get_page(page)

    context = {
        'watki': watki,
        'page': page
    }

    return render(request, 'apsi_app/forum/forum.html', context)


def dodaj_watek(request):
    if request.method == 'POST':
        watek_form = WatekForm(request.POST)

        if watek_form.is_valid():
            with transaction.atomic():
                watek = watek_form.save(commit=False)
                watek.uzytkownik = request.user
                watek.save()

                wpis1 = ForumPost(tresc=watek_form.cleaned_data['tresc'], uzytkownik=request.user, watek=watek)
                wpis1.save()

            return redirect(reverse('watek')+f"?watek_id={watek.id}")
        else:
            print('form invalid')

    watek_form = WatekForm()

    context = {
        'watek_form': watek_form,
    }

    return render(request, 'apsi_app/forum/dodaj-watek.html', context)


def watek(request):
    watek_id = request.GET['watek_id']
    watek = Watek.objects.get(id=watek_id)

    if request.method == 'POST':
        tresc = request.POST['tresc']
        wpis = ForumPost(tresc=tresc, uzytkownik=request.user, watek=watek)
        wpis.save()

    wpisy = ForumPost.objects.filter(watek=watek_id)

    context = {
        'watek': watek,
        'wpisy': wpisy,
    }

    return render(request, 'apsi_app/forum/watek.html', context)
