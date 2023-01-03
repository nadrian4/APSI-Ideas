from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile', views.profile, name='profile'),
    path('dodaj-pomysl', views.dodaj_pomysl, name='dodaj-pomysl'),
    path('usun-pomysl', views.usun_pomysl, name='usun-pomysl'),
    path('glosowania', views.glosowania, name='glosowania'),
    path('utworz-glosowanie', views.utworz_glosowanie, name='utworz-glosowanie'),
    path('strona-glosowania', views.strona_glosowania, name='strona-glosowania'),
    path('usun-glosowanie', views.usun_glosowanie, name='usun-glosowanie'),
    path('komentarze', views.komentarze, name='komentarze'),
    path('dodaj-komentarz', views.dodaj_komentarz, name='dodaj-komentarz'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
