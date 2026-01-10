from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    # On affiche seulement ces 3 colonnes qui existent déjà
    list_display = ('name', 'email', 'date_created') 
    # On ajoute une recherche par nom ou email
    search_fields = ('name', 'email')