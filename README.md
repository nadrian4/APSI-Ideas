# APSI-Ideas
Projekt realizowany w semestrze 2022Z w ramach przedmiotu APSI

## Instrukcja uruchomienia
### Zmienna środowiskowa SECRET_KEY
SECRET-KEY nie może być w kodzie. Musi być w zmiennej środowiskowej. W Windows można dodać zmienną użytkownika i się zalogować ponownie, wtedy będzie aktywna.

SECRET-KEY można wziąć z nowego projektu django: `django-admin startproject tt` i z pliku `settings.py` w linii `SECRET_KEY`.

### Stworzenie środowiska python
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Baza danych, stworzenie admina, uruchomienie serwera
```
python app/manage.py makemigrations apsi_app
python app/manage.py migrate apsi_app
python app/manage.py migrate

python app/manage.py createsuperuser

python app/manage.py runserver
```

## Dodatkowe informacje
### Baza danych
Używana baza danych: SQLite
