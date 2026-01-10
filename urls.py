# config/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
# On importe uniquement ce qui existe vraiment dans ton fichier views.py
from messagerie.views import page_accueil, enregistrer_message

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', page_accueil, name='accueil'),
    
    # ⚠️ TRÈS IMPORTANT : L'adresse ici doit être la même que dans ton JavaScript (fetch)
    # Si ton JS utilise '/envoyer-contact/', alors écris 'envoyer-contact/' ici.
    path('envoyer-contact/', enregistrer_message, name='enregistrer_message'),
]

# Servir les fichiers statiques (images, CSS)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])