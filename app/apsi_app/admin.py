from django.contrib import admin

from apsi_app.models import Konkurs, Glosowanie, Ocena, Pomysl, Komentarz, Watek, ForumPost

admin.site.register(Konkurs)
admin.site.register(Pomysl)
admin.site.register(Ocena)
admin.site.register(Glosowanie)
admin.site.register(Komentarz)
admin.site.register(Watek)
admin.site.register(ForumPost)
