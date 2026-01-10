import json
import logging
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

@csrf_exempt
@require_http_methods(["POST"])
def enregistrer_message(request):
    """
    Reçoit les données du formulaire de contact et envoie des emails
    """
    try:
        # 1. Parser les données JSON
        try:
            data = json.loads(request.body)
            logger.info(f"📥 Données reçues: {data}")
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

        if not nom or not email or not message:
            logger.warning(f"⚠️ Champs manquants - Nom: {nom}, Email: {email}, Message: {message}")
            return JsonResponse(
                {"success": False, "message": "Les champs nom, email et message sont obligatoires"},
                status=400
            )

        # 3. Valider le format email basique
        if '@' not in email or '.' not in email:
            logger.warning(f"⚠️ Email invalide: {email}")
            return JsonResponse(
                {"success": False, "message": "Format email invalide"},
                status=400
            )

        # 4. Préparer les emails
        try:
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
            
            # Essayer d'envoyer l'email à l'ASBL
            try:
                send_mail(
                    subject=sujet_asbl,
                    message=corps_asbl,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=['uzimamzenon@gmail.com'],
                    fail_silently=False,
                )
                logger.info("✅ Email ASBL envoyé avec succès")
                email_asbl_sent = True
            except Exception as e:
                logger.error(f"⚠️ Erreur envoi email ASBL: {type(e).__name__}: {e}")
                email_asbl_sent = False

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
                logger.info(f"✅ Email confirmation envoyé à {email}")
                email_confirm_sent = True
            except Exception as e:
                logger.error(f"⚠️ Erreur envoi email confirmation: {type(e).__name__}: {e}")
                email_confirm_sent = False

            # Vérifier qu'au moins un email a été envoyé
            if email_asbl_sent or email_confirm_sent:
                response_message = "✅ Merci! Votre message a été enregistré."
                if not email_confirm_sent:
                    response_message += " (Confirmation email échouée)"
                
                logger.info(f"✅ Formulaire traité avec succès pour {email}")
                return JsonResponse(
                    {"success": True, "message": response_message},
                    status=201
                )
            else:
                logger.error("❌ Aucun email n'a pu être envoyé")
                return JsonResponse(
                    {"success": False, "message": "Erreur lors de l'envoi des emails"},
                    status=500
                )

        except Exception as e:
            logger.error(f"❌ Erreur critique email: {type(e).__name__}: {e}", exc_info=True)
            return JsonResponse(
                {"success": False, "message": f"Erreur serveur: {str(e)}"},
                status=500
            )

    except Exception as e:
        logger.error(f"❌ Erreur non gérée: {type(e).__name__}: {e}", exc_info=True)
        return JsonResponse(
            {"success": False, "message": "Erreur serveur interne"},
            status=500
        )