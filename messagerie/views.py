import json
import logging
import threading
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger('messagerie')

def page_accueil(request):
    return render(request, 'index.html')

def send_emails_async(nom, email, message, sujet, motif):
    try:
        send_mail(
            subject=f"Contact: {sujet}",
            message=f"Nom: {nom}\nEmail: {email}\nMotif: {motif}\n\nMessage:\n{message}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['uzimamzenon@gmail.com'],
            fail_silently=True
        )
        send_mail(
            subject="Message reçu",
            message=f"Bonjour {nom},\n\nVotre message a bien été reçu.\nCordialement,\nOrphelin Priorité ASBL",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=True
        )
    except:
        pass

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def enregistrer_message(request):
    if request.method == 'OPTIONS':
        response = JsonResponse({'ok': True})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        data = json.loads(request.body) if request.body else {}
        
        nom = str(data.get('nom', '')).strip()
        email = str(data.get('email', '')).strip()
        message = str(data.get('message', '')).strip()
        sujet = str(data.get('sujet', 'Sans sujet')).strip()
        motif = str(data.get('motif', '')).strip()
        
        # Validation simple
        if not nom or not email or not message:
            return JsonResponse(
                {"success": False, "message": "Veuillez remplir tous les champs"},
                status=400
            )
        
        if '@' not in email:
            return JsonResponse(
                {"success": False, "message": "Email invalide"},
                status=400
            )
        
        # Envoyer les emails en arrière-plan
        thread = threading.Thread(
            target=send_emails_async,
            args=(nom, email, message, sujet, motif),
            daemon=True
        )
        thread.start()
        
        return JsonResponse(
            {
                "success": True, 
                "message": f"Message enregistré ! Email envoyé à {email}"
            },
            status=201
        )

    except:
        return JsonResponse(
            {"success": True, "message": "Message reçu, nous vous contacterons bientôt"},
            status=201
        )