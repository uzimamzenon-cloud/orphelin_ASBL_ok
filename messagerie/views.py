import json
import logging
import threading
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Configure le logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def page_accueil(request):
    """Affiche la page d'accueil"""
    try:
        logger.info("✅ Page accueil chargée")
        return render(request, 'index.html')
    except Exception as e:
        logger.error(f"❌ Erreur page accueil: {e}", exc_info=True)
        return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

def send_emails_async(nom, email, message, sujet, motif):
    """Envoie les emails de manière asynchrone et robuste"""
    try:
        logger.info(f"🚀 Thread d'envoi: début pour {email}")
        
        # Email à l'ASBL
        try:
            send_mail(
                subject=f"📬 Contact: {sujet} ({nom})",
                message=f"Nom: {nom}\nEmail: {email}\nMotif: {motif}\n\nMessage:\n{message}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['uzimamzenon@gmail.com'],
                fail_silently=True,
                timeout=30
            )
            logger.info(f"✅ Email ASBL envoyé à uzimamzenon@gmail.com")
        except Exception as e:
            logger.error(f"❌ Erreur envoi ASBL: {type(e).__name__}: {e}")

        # Email confirmation
        try:
            send_mail(
                subject="✅ Message reçu - Orphelin Priorité ASBL",
                message=f"Bonjour {nom},\n\nVotre message a bien été reçu par Orphelin Priorité ASBL.\nNous vous répondrons dans les meilleurs délais.\n\nCordialement,\nL'équipe Orphelin Priorité ASBL",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=True,
                timeout=30
            )
            logger.info(f"✅ Email confirmation envoyé à {email}")
        except Exception as e:
            logger.error(f"❌ Erreur envoi confirmation: {type(e).__name__}: {e}")
            
        logger.info(f"✅ Thread d'envoi: fin pour {email}")
    except Exception as e:
        logger.error(f"❌ Erreur générale send_emails_async: {type(e).__name__}: {e}", exc_info=True)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def enregistrer_message(request):
    """Traite le formulaire de contact"""
    
    logger.info(f"📨 Requête reçue: {request.method} {request.path}")
    
    if request.method == 'OPTIONS':
        logger.debug("✅ CORS OPTIONS accepté")
        response = JsonResponse({'ok': True})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
        return response
    
    try:
        # Parser JSON
        if not request.body:
            logger.warning("⚠️ Body vide")
            return JsonResponse({"success": False, "message": "❌ Données manquantes"}, status=400)
            
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON invalide: {e}")
            return JsonResponse({"success": False, "message": "❌ Format JSON invalide"}, status=400)
        
        logger.debug(f"📦 Data reçue: {data}")
        
        # Récupérer les données
        nom = str(data.get('nom', '')).strip()
        email = str(data.get('email', '')).strip()
        message = str(data.get('message', '')).strip()
        sujet = str(data.get('sujet', 'Sans sujet')).strip()
        motif = str(data.get('motif', '')).strip()
        
        logger.info(f"📋 Formulaire: nom='{nom}', email='{email}', sujet='{sujet}', msg_len={len(message)}")
        
        # Validation des champs obligatoires
        if not nom:
            logger.warning("⚠️ Nom manquant")
            return JsonResponse({"success": False, "message": "❌ Nom requis"}, status=400)
        
        if not email:
            logger.warning("⚠️ Email manquant")
            return JsonResponse({"success": False, "message": "❌ Email requis"}, status=400)
        
        if not message:
            logger.warning("⚠️ Message manquant")
            return JsonResponse({"success": False, "message": "❌ Message requis"}, status=400)
        
        # Validation de l'email
        if '@' not in email or '.' not in email:
            logger.warning(f"⚠️ Email invalide: {email}")
            return JsonResponse({"success": False, "message": "❌ Email invalide"}, status=400)
        
        # Lancer l'envoi d'emails en arrière-plan (non-bloquant)
        logger.info(f"🚀 Lancement du thread pour {email}")
        thread = threading.Thread(
            target=send_emails_async,
            args=(nom, email, message, sujet, motif),
            daemon=True
        )
        thread.start()
        
        # Répondre IMMÉDIATEMENT au client
        success_message = f"✅ Message reçu ! Nous vous répondrons à {email}"
        logger.info(f"📤 Réponse 201 au client: {success_message}")
        
        return JsonResponse(
            {
                "success": True, 
                "message": success_message
            },
            status=201
        )

    except Exception as e:
        logger.error(f"❌ Erreur non gérée: {type(e).__name__}: {e}", exc_info=True)
        return JsonResponse(
            {"success": False, "message": f"❌ Erreur serveur: {str(e)[:100]}"},
            status=500
        )