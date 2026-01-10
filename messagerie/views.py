import json
import logging
import threading
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Logger pour les erreurs
logger = logging.getLogger(__name__)

def page_accueil(request):
    """Affiche la page d'accueil"""
    try:
        return render(request, 'index.html')
    except Exception as e:
        logger.error(f"❌ Erreur page accueil: {e}")
        return JsonResponse({"error": str(e)}, status=500)

def send_emails_async(nom, email, message, sujet, motif):
    """
    Envoie les emails en arrière-plan (thread séparé)
    pour ne pas bloquer la réponse HTTP
    """
    try:
        logger.info(f"📧 [ASYNC] Début envoi des emails pour {email}")
        
        # Email vers l'ASBL
        sujet_asbl = f"📬 Contact ASBL: {sujet} ({nom})"
        corps_asbl = f"""Nouveau message de contact reçu sur le site:

👤 NOM: {nom}
📧 EMAIL: {email}
🎯 MOTIF: {motif}
📝 SUJET: {sujet}

MESSAGE:
{message}

---
Envoyé par le formulaire de contact du site
"""
        
        try:
            send_mail(
                subject=sujet_asbl,
                message=corps_asbl,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['uzimamzenon@gmail.com'],
                fail_silently=False,
            )
            logger.info(f"✅ [ASYNC] Email ASBL envoyé avec succès")
        except Exception as e:
            logger.error(f"⚠️ [ASYNC] Erreur envoi email ASBL: {type(e).__name__}: {e}")

        # Email de confirmation au visiteur
        sujet_confirm = f"✅ Nous avons reçu votre message"
        corps_confirm = f"""Bonjour {nom},

Merci de nous avoir contactés! Votre message a bien été reçu par Orphelin Priorité ASBL.

Nous vous répondrons dans les meilleurs délais.

Cordialement,
Orphelin Priorité ASBL
"""
        
        try:
            send_mail(
                subject=sujet_confirm,
                message=corps_confirm,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"✅ [ASYNC] Email confirmation envoyé à {email}")
        except Exception as e:
            logger.error(f"⚠️ [ASYNC] Erreur envoi email confirmation: {type(e).__name__}: {e}")
        
        logger.info(f"✅ [ASYNC] Fin envoi des emails")
            
    except Exception as e:
        logger.error(f"❌ [ASYNC] Erreur critique dans send_emails_async: {type(e).__name__}: {e}", exc_info=True)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def enregistrer_message(request):
    """
    Reçoit les données du formulaire de contact et envoie des emails
    Les emails sont envoyés en arrière-plan pour ne pas bloquer la réponse
    """
    
    # Gérer les requêtes OPTIONS pour CORS
    if request.method == 'OPTIONS':
        response = JsonResponse({'status': 'ok'})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
        return response
    
    logger.info("=" * 60)
    logger.info("📨 NOUVELLE REQUÊTE DE FORMULAIRE")
    logger.info("=" * 60)
    
    try:
        # 1. Parser les données JSON
        logger.info(f"📥 Request body size: {len(request.body)} bytes")
        
        try:
            data = json.loads(request.body)
            logger.info(f"✅ JSON parsé correctement")
            logger.info(f"📦 Données reçues: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON invalide: {e}")
            return JsonResponse(
                {"success": False, "message": "Format JSON invalide"},
                status=400
            )

        # 2. Valider les champs obligatoires
        nom = data.get('nom', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()
        sujet = data.get('sujet', 'Sans sujet').strip()
        motif = data.get('motif', 'Non spécifié').strip()

        logger.info(f"✓ Nom: {nom or 'VIDE'}")
        logger.info(f"✓ Email: {email or 'VIDE'}")
        logger.info(f"✓ Message: {message[:50] if message else 'VIDE'}...")

        if not nom or not email or not message:
            logger.warning(f"⚠️ VALIDATION ÉCHOUÉE - Champs manquants")
            return JsonResponse(
                {"success": False, "message": "Les champs nom, email et message sont obligatoires"},
                status=400
            )

        # 3. Valider le format email basique
        if '@' not in email or '.' not in email:
            logger.warning(f"⚠️ EMAIL INVALIDE: {email}")
            return JsonResponse(
                {"success": False, "message": "Format email invalide"},
                status=400
            )

        logger.info(f"✅ VALIDATION RÉUSSIE - Lancement envoi async...")
        
        # 4. Lancer l'envoi des emails en arrière-plan (NON-BLOQUANT)
        email_thread = threading.Thread(
            target=send_emails_async,
            args=(nom, email, message, sujet, motif),
            daemon=True
        )
        email_thread.start()
        logger.info(f"✅ Thread d'envoi lancé")
        
        # Retourner immédiatement sans attendre les emails
        response_data = {
            "success": True, 
            "message": "✅ Merci! Votre message a été enregistré. Vous recevrez un email de confirmation."
        }
        logger.info(f"✅ RÉPONSE 201 ENVOYÉE: {response_data}")
        logger.info("=" * 60)
        
        return JsonResponse(response_data, status=201)

    except Exception as e:
        logger.error(f"❌ ERREUR NON GÉRÉE: {type(e).__name__}: {e}", exc_info=True)
        logger.info("=" * 60)
        return JsonResponse(
            {"success": False, "message": "Erreur serveur interne"},
            status=500
        )