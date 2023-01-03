from django import forms

class LoginForm(forms.Form):
    uzytkownik = forms.CharField(label='Użytkownik', max_length=20)
    haslo = forms.CharField(label='Hasło', max_length=20)