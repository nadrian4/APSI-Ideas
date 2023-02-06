from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

from .forms import LoginForm

def login_apsi(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        
        if login_form.is_valid():
            uzytkownik = login_form.cleaned_data['uzytkownik']
            haslo = login_form.cleaned_data['haslo']
            konto = authenticate(request, username=uzytkownik, password=haslo)

            if konto:
                login(request, konto)
                
                return redirect('index')
            else:
                return redirect('login')
    else:
        login_form = LoginForm()

    return render(request, 'apsi_auth/login.html', {'login_form': login_form})
