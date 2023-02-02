from django import forms

from .models import KATEGORIE, ROLE, Pomysl
from django.contrib.auth.models import User


class PomyslForm(forms.ModelForm):
    tytul = forms.CharField(max_length=20)
    tresc = forms.CharField(max_length=200)
    planowane_korzysci = forms.CharField(max_length=200)
    planowane_koszty = forms.FloatField()
    kategoria = forms.ChoiceField(choices=KATEGORIE)
    kto_moze_oceniac = forms.ChoiceField(choices=ROLE)
    plik = forms.ImageField(required=False)

    class Meta:
        model = Pomysl
        fields = ['tytul', 'tresc', 'planowane_korzysci', 'planowane_koszty', 'kategoria', 'kto_moze_oceniac', 'plik']