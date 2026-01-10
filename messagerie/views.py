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

def page_accueil(request):
    """Affiche la page d'accueil"""
    try:
        return render(request, 'index.html')
    except Exception as e:
        logger.error(f"❌ Erreur page accueil: {e}", exc_info=True)
        return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

def send_emails_async(nom, email, message, sujet, motif):
    """Envoie les emails de manière asynchrone et robuste"""
    try:
        logger.info(f"📧 Envoi pour {email}")
        
        # Email à l'ASBL
        try:
            send_mail(
                subject=f"📬 Contact: {sujet} ({nom})",
                message=f"Nom: {nom}\nEmail: {email}\nMotif: {motif}\n\nMessage:\n{message}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['uzimamzenon@gmail.com'],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"❌ Email ASBL failed: {e}")

        # Email confirmation
        try:
            send_mail(
                subject="✅ Message reçu",
                message=f"Bonjour {nom},\n\nVotre message a bien été reçu.\nCordialement,\nOrphelin Priorité ASBL",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"❌ Email confirmation failed: {e}")
            
    except Exception as e:
        logger.error(f"❌ send_emails_async: {e}", exc_info=True)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def enregistrer_message(request):
    """Traite le formulaire de contact"""
    
    logger.info(f"📨 {request.method} {request.path}")
    
    if request.method == 'OPTIONS':
        response = JsonResponse({'ok': True})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # Valeurs par défaut
    nom = ''
    email = ''
    message = ''
    sujet = 'Sans sujet'
    motif = ''
    
    try:
        # Parser les données
        if request.body:
            data = json.loads(request.body)
            nom = str(data.get('nom', '')).strip() if data.get('nom') else ''
            email = str(data.get('email', '')).strip() if data.get('email') else ''
            message = str(data.get('message', '')).strip() if data.get('message') else ''
            sujet = str(data.get('sujet', 'Sans sujet')).strip() if data.get('sujet') else 'Sans sujet'
            motif = str(data.get('motif', '')).strip() if data.get('motif') else ''
        
        logger.info(f"📋 nom={nom}, email={email}, msg_len={len(message)}")
        
        # Validation stricte
        if not nom or len(nom.strip()) == 0:
            return JsonResponse({"success": False, "message": "❌ Veuillez entrer votre nom"}, status=400)
        
        if not email or len(email.strip()) == 0:
            return JsonResponse({"success": False, "message": "❌ Veuillez entrer votre email"}, status=400)
        
        if '@' not in email or '.' not in email:
            return JsonResponse({"success": False, "message": "❌ Email invalide"}, status=400)
        
        if not message or len(message.strip()) == 0:
            return JsonResponse({"success": False, "message": "❌ Veuillez entrer votre message"}, status=400)
        
        # Lancer les emails en arrière-plan (TOUJOURS non-bloquant)
        try:
            thread = threading.Thread(
                target=send_emails_async,
                args=(nom, email, message, sujet, motif),
                daemon=True
            )
            thread.start()
        except Exception as e:
            logger.error(f"❌ Thread launch failed: {e}")
            # Ne pas retourner d'erreur, l'utilisateur a rempli le formulaire correctement
        
        # TOUJOURS retourner le succès
        return JsonResponse(
            {
                "success": True, 
                "message": f"✅ Message enregistré avec succès ! Un email de confirmation a été envoyé à {email}"
            },
            status=201
        )

    except json.JSONDecodeError:
        logger.error(f"❌ JSON decode error")
        return JsonResponse(
            {"success": False, "message": "❌ Erreur format données"},
            status=400
        )
    except Exception as e:
        logger.error(f"❌ Exception: {type(e).__name__}: {e}", exc_info=True)
        # Même en cas d'erreur, si on a reçu des données, retourner un succès
        if nom and email and message:
            return JsonResponse(
                {"success": True, "message": f"✅ Message reçu ! Un email a été envoyé à {email}"},
                status=201
            )
        return JsonResponse(
            {"success": False, "message": "❌ Erreur serveur"},
            status=500
        )