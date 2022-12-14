from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

KATEGORIE = (
    ('Edukacja', 'Edukacja'),
    ('Życie społeczne', 'Życie społeczne'),
    ('Infrastruktura', 'Infrastruktura'),
)
ROLE = (
    ('Student', 'Student'),
    ('Pracownik', 'Pracownik'),
    ('Wszyscy', 'Wszyscy'),
)


class Konkurs(models.Model):
    nazwa = models.CharField(max_length=20)
    data_koniec = models.DateField()

    def __str__(self):
        return self.nazwa


class Glosowanie(models.Model):
    nazwa = models.CharField(max_length=20)
    max_glos = models.IntegerField()
    data_koniec = models.DateField()

    def __str__(self):
        return self.nazwa


class Pomysl(models.Model):
    tytul = models.CharField(max_length=20)
    tresc = models.CharField(max_length=200)
    kategoria = models.CharField(max_length=20, choices=KATEGORIE)
    kto_moze_oceniac = models.CharField(max_length=20, choices=ROLE)
    plik = models.ImageField(upload_to='app/apsi_app/pliki/pomysl-pliki', null=True)
    data = models.DateField(default=timezone.now)
    srednia_ocen = models.IntegerField(default=0)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)
    konkurs = models.ForeignKey(Konkurs, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.tytul


class GlosowaniePomysl(models.Model):
    glosowanie = models.ForeignKey(Glosowanie, on_delete=models.CASCADE)
    pomysl = models.ForeignKey(Pomysl, on_delete=models.CASCADE)
    srednia_glosow = models.FloatField()


class Glos(models.Model):
    glosowanie = models.ForeignKey(Glosowanie, on_delete=models.CASCADE)
    pomysl = models.ForeignKey(Pomysl, on_delete=models.CASCADE)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)
    glos = models.IntegerField()

class Komentarz(models.Model):
    tresc = models.CharField(max_length=200)
    data = models.DateTimeField(default=timezone.now)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)
    rodzic = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    pomysl = models.ForeignKey(Pomysl, on_delete=models.CASCADE)

    def get_children_with_depths(self, depth=0):
        r = []
        r.append([self, depth])
        for c in Komentarz.objects.filter(rodzic=self):
            _r = c.get_children_with_depths(depth=depth+1)
            if 0 < len(_r):
                r.extend(_r)
        return r

    def __str__(self):
        return self.tresc

class Ocena(models.Model):
    ocena = models.IntegerField()
    pomysl = models.ForeignKey(Pomysl, on_delete=models.CASCADE)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.pomysl.__str__() + ', ' + str(self.ocena)
