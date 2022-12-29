from django.contrib import admin

from apsi_app.models import Glosowanie, Ocena, Pomysl

admin.site.register(Pomysl)
admin.site.register(Ocena)
admin.site.register(Glosowanie)
