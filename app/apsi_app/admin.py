from django.contrib import admin

from apsi_app.models import Glosowanie, Ocena, Pomysl, Komentarz

admin.site.register(Pomysl)
admin.site.register(Ocena)
admin.site.register(Glosowanie)
admin.site.register(Komentarz)
