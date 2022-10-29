from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Pomysl(models.Model):
    tytul = models.CharField(max_length=20)
    tresc = models.CharField(max_length=200)
    data = models.DateField(default=timezone.now)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.tytul
