from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def login_apsi(request):
    if request.method == 'POST':
        uzytkownik = request.POST['uzytkownik']
        haslo = request.POST['haslo']
        konto = authenticate(request, username=uzytkownik, password=haslo)

        if konto is not None:
            login(request, konto)
            return redirect('index')
        else:
            return redirect('login')
    else:
        return render(request, 'apsi_auth/login.html', {})
