from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Glosowanie(models.Model):
    nazwa = models.CharField(max_length=20)
    max_ocena = models.IntegerField()

    def __str__(self):
            return self.nazwa


class Pomysl(models.Model):
    tytul = models.CharField(max_length=20)
    tresc = models.CharField(max_length=200)
    data = models.DateField(default=timezone.now)
    srednia_ocen = models.IntegerField(default=0)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.tytul


class GlosowaniePomysl(models.Model):
    glosowanie = models.ForeignKey(Glosowanie, on_delete=models.CASCADE)
    pomysl = models.ForeignKey(Pomysl, on_delete=models.CASCADE)


class Ocena(models.Model):
    ocena = models.IntegerField()
    pomysl = models.ForeignKey(Pomysl, on_delete=models.CASCADE)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.pomysl.__str__() + ', ' + str(self.ocena)
