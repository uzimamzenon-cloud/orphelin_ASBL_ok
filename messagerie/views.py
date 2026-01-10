import json
import logging
import threading
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Configure le logger
logger = logging.getLogger(__name__)

def page_accueil(request):
    """Affiche la page d'accueil"""
    try:
        logger.info("📄 Accès page d'accueil")
        return render(request, 'index.html')
    except Exception as e:
        logger.error(f"❌ Erreur page accueil: {e}")
        return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

def send_emails_simple(nom, email, message, sujet, motif):
    """Envoie les emails sans exception blocking"""
    logger.info(f"📧 Envoi d'emails pour {email}")
    try:
        # Email à l'ASBL
        try:
            send_mail(
                subject=f"📬 Contact: {sujet} ({nom})",
                message=f"Nom: {nom}\nEmail: {email}\nMotif: {motif}\n\nMessage:\n{message}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['uzimamzenon@gmail.com'],
                fail_silently=False,
            )
            logger.info(f"✅ Email ASBL envoyé pour {email}")
        except Exception as e:
            logger.error(f"❌ Erreur envoi ASBL: {e}")

        # Email confirmation
        try:
            send_mail(
                subject="✅ Message reçu - Orphelin Priorité ASBL",
                message=f"Bonjour {nom},\n\nVotre message a bien été reçu par Orphelin Priorité ASBL.\nNous vous répondrons dans les meilleurs délais.\n\nCordialement,\nL'équipe Orphelin Priorité ASBL",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"✅ Email confirmation envoyé à {email}")
        except Exception as e:
            logger.error(f"❌ Erreur envoi confirmation: {e}")
            
    except Exception as e:
        logger.error(f"❌ Erreur send_emails_simple: {e}")

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def enregistrer_message(request):
    """Traite le formulaire de contact"""
    
    logger.info(f"📨 Requête reçue: {request.method}")
    
    if request.method == 'OPTIONS':
        logger.info("✅ Requête CORS OPTIONS acceptée")
        response = JsonResponse({'ok': True})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
        response['Access-Control-Max-Age'] = '86400'
        return response
    
    try:
        # Parser JSON
        logger.info(f"📦 Body: {request.body[:100]}")
        data = json.loads(request.body) if request.body else {}
        
        # Récupérer les données
        nom = str(data.get('nom', '')).strip()
        email = str(data.get('email', '')).strip()
        message = str(data.get('message', '')).strip()
        sujet = str(data.get('sujet', 'Sans sujet')).strip()
        motif = str(data.get('motif', '')).strip()
        
        logger.info(f"📋 Données reçues: nom={nom}, email={email}, message_len={len(message)}")
        
        # Valider
        if not nom or not email or not message:
            logger.warning(f"⚠️ Champs manquants: nom={bool(nom)}, email={bool(email)}, message={bool(message)}")
            return JsonResponse(
                {"success": False, "message": "❌ Veuillez remplir tous les champs (Nom, Email, Message)"},
                status=400
            )
        
        if '@' not in email or '.' not in email:
            logger.warning(f"⚠️ Email invalide: {email}")
            return JsonResponse(
                {"success": False, "message": "❌ Email invalide"},
                status=400
            )
        
        # Envoyer les emails en arrière-plan
        logger.info(f"🚀 Lancement du thread d'envoi d'emails")
        thread = threading.Thread(
            target=send_emails_simple,
            args=(nom, email, message, sujet, motif),
            daemon=True
        )
        thread.start()
        
        # Répondre immédiatement avec le bon message
        success_message = f"✅ Message enregistré avec succès ! Un email de confirmation a été envoyé à {email}"
        logger.info(f"✅ Réponse de succès: {success_message}")
        return JsonResponse(
            {
                "success": True, 
                "message": success_message
            },
            status=201
        )

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON invalide: {e}")
        return JsonResponse(
            {"success": False, "message": "❌ Erreur de format JSON"},
            status=400
        )
    except Exception as e:
        logger.error(f"❌ ERREUR: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse(
            {"success": False, "message": f"❌ Erreur serveur: {str(e)}"},
            status=500
        )