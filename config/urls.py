from django.contrib import admin
from django.urls import path
from messagerie.views import page_accueil, enregistrer_message

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', page_accueil, name='accueil'),
    path('envoyer-contact/', enregistrer_message),
]