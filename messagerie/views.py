import json
import threading
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ContactMessage # <--- INDISPENSABLE POUR STOCKER

def page_accueil(request):
    return render(request, 'index.html')

def send_emails_async(nom, email, message, sujet, motif):
    """Envoie les emails sans bloquer la réponse de l'utilisateur"""
    
    # 1. Email pour les responsables de l'ASBL
    try:
        send_mail(
            subject=f"Contact ASBL: {sujet}",
            message=f"Nouvelle demande sur le site !\n\nNom: {nom}\nEmail: {email}\nMotif: {motif}\n\nMessage:\n{message}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['uzimamzenon@gmail.com', 'desirekibikibi12@gmail.com'],
            fail_silently=True
        )
    except Exception:
        pass
    
    # 2. Email de confirmation automatique pour le visiteur
    try:
        send_mail(
            subject="Accusé de réception - Orphelin Priorité ASBL",
            message=f"Bonjour {nom},\n\nNous avons bien reçu votre message concernant : '{motif}'.\nNotre équipe vous répondra très prochainement.\n\nCordialement,\nOrphelin Priorité ASBL",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=True
        )
    except Exception:
        pass

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def enregistrer_message(request):
    """Endpoint pour recevoir, stocker et envoyer les notifications"""
    
    # Gestion du CORS (pour autoriser l'envoi depuis ton site)
    if request.method == 'OPTIONS':
        response = JsonResponse({'ok': True})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
        return response
    
    try:
        # Récupération des données JSON envoyées par le JavaScript
        data = json.loads(request.body) if request.body else {}
        
        # Nettoyage des données (Strip)
        nom = str(data.get('nom', '')).strip()
        email = str(data.get('email', '')).strip()
        sujet = str(data.get('sujet', 'Sans sujet')).strip()
        motif = str(data.get('motif', '')).strip()
        message = str(data.get('message', '')).strip()
        
        # Validation simple
        if not nom or not email or not message:
            return JsonResponse({"success": False, "message": "Oups ! Remplissez tous les champs obligatoires."}, status=400)
        
        if '@' not in email:
            return JsonResponse({"success": False, "message": "L'adresse Email n'est pas correcte."}, status=400)

        # --- ÉTAPE CRUCIALE : ENREGISTREMENT DANS LA BASE DE DONNÉES ---
        ContactMessage.objects.create(
            name=nom,        # Ton champ dans models.py s'appelle 'name'
            email=email,
            subject=sujet,   # Ton champ dans models.py s'appelle 'subject'
            reason=motif,    # Ton champ dans models.py s'appelle 'reason'
            message=message
        )

        # --- ENVOI DES EMAILS EN ARRIÈRE-PLAN ---
        # Le thread permet au site de répondre "Succès" sans attendre que Gmail ait fini
        threading.Thread(
            target=send_emails_async,
            args=(nom, email, message, sujet, motif),
            daemon=True
        ).start()
        
        return JsonResponse({
            "success": True, 
            "message": f"✅ C'est réussi {nom} ! Ton message est enregistré et l'e-mail a été envoyé aux responsables."
        }, status=201)

    except Exception as e:
        # Si une erreur survient, on renvoie le message d'erreur
        return JsonResponse({"success": False, "message": f"Erreur serveur: {str(e)}"}, status=500)