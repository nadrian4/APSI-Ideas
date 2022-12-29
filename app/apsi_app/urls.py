from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile', views.profile, name='profile'),
    path('dodaj-pomysl', views.dodaj_pomysl, name='dodaj-pomysl'),
    path('glosowania', views.glosowania, name='glosowania'),
    path('utworz-glosowanie', views.utworz_glosowanie, name='utworz-glosowanie'),
    path('strona-glosowania', views.strona_glosowania, name='strona-glosowania'),
    path('usun-glosowanie', views.usun_glosowanie, name='usun-glosowanie'),
]
