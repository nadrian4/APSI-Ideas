# APSI-Ideas
Projekt realizowany w semestrze 2022Z w ramach przedmiotu APSI

## Uruchomienie strony

### Zmienna środowiskowa SECRET_KEY
SECRET-KEY nie może być w kodzie. Musi być w zmiennej środowiskowej. W Windows można dodać zmienną użytkownika i się zalogować ponownie, wtedy będzie aktywna.

SECRET-KEY można wziąć z nowego projektu django: `django-admin startproject tt` i z pliku `settings.py` w linii `SECRET_KEY`.

### Baza postgres
Stworzyć bazę postgres o nazwie `apsi` z użytkownikiem `postgres` i hasłem `123`. Baza na domyślnym porcie `5432`.

### Środowisko python
```
python -m venv venv
.\venv\Scripts\activate
pip install Django psycopg2
```

### Przygotowanie bazy
W `APSI-Ideas`:
```
python manage.py makemigrations apsi_app
python manage.py migrate
```

### Administrator strony
W `APSI-Ideas`: `python manage.py createsuperuser`

### Uruchomienie strony
W `APSI-Ideas` komenda `python manage.py runserver`.

### Dodanie danych do bazy
Na panelu `/admin` można dodać wiersze do tabeli pomysły. Wtedy na głównej stronie będzie lista tych pomysłów.

## docker
Uruchomienie w nowym środowisku (flaga -d powoduje uruchomienie kontenera w tle):
1. docker-compose up -d

Usunięcie zbudowanego kontenera i ponowne uruchomienie
1. docker-compose down 
2. docker rm -f $(docker ps -a -q) 
3. docker volume rm $(docker volume ls -q)
4. docker-compose up -d 


