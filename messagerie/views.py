import json
import logging
import threading
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

def page_accueil(request):
    """Affiche la page d'accueil"""
    try:
        return render(request, 'index.html')
    except Exception as e:
        logger.error(f"Erreur page accueil: {e}")
        return JsonResponse({"error": str(e)}, status=500)

def send_emails_simple(nom, email, message, sujet, motif):
    """Envoie les emails sans exception blocking"""
    try:
        # Email à l'ASBL
        try:
            send_mail(
                subject=f"Contact: {sujet} ({nom})",
                message=f"Nom: {nom}\nEmail: {email}\nMotif: {motif}\n\nMessage:\n{message}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['uzimamzenon@gmail.com'],
                fail_silently=True,
            )
            logger.info(f"Email ASBL envoyé pour {email}")
        except Exception as e:
            logger.error(f"Erreur envoi ASBL: {e}")

        # Email confirmation
        try:
            send_mail(
                subject="Message reçu",
                message=f"Bonjour {nom},\n\nVotre message a bien été reçu.\n\nCordialement,\nOrphelin Priorité ASBL",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=True,
            )
            logger.info(f"Email confirmation envoyé à {email}")
        except Exception as e:
            logger.error(f"Erreur envoi confirmation: {e}")
            
    except Exception as e:
        logger.error(f"Erreur send_emails_simple: {e}")

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def enregistrer_message(request):
    """Traite le formulaire de contact"""
    
    if request.method == 'OPTIONS':
        response = JsonResponse({'ok': True})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        # Parser JSON
        data = json.loads(request.body) if request.body else {}
        
        # Récupérer les données
        nom = str(data.get('nom', '')).strip()
        email = str(data.get('email', '')).strip()
        message = str(data.get('message', '')).strip()
        sujet = str(data.get('sujet', 'Sans sujet')).strip()
        motif = str(data.get('motif', '')).strip()
        
        # Valider
        if not nom or not email or not message:
            return JsonResponse(
                {"success": False, "message": "Champs obligatoires manquants"},
                status=400
            )
        
        if '@' not in email:
            return JsonResponse(
                {"success": False, "message": "Email invalide"},
                status=400
            )
        
        # Envoyer les emails en arrière-plan
        thread = threading.Thread(
            target=send_emails_simple,
            args=(nom, email, message, sujet, motif),
            daemon=True
        )
        thread.start()
        
        # Répondre immédiatement
        return JsonResponse(
            {"success": True, "message": "Message enregistré avec succès"},
            status=201
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "JSON invalide"},
            status=400
        )
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return JsonResponse(
            {"success": False, "message": "Erreur serveur"},
            status=500
        )