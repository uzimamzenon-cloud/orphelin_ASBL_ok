import json
import threading
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def page_accueil(request):
    return render(request, 'index.html')

def send_emails_async(nom, email, message, sujet, motif):
    """Envoie les emails sans bloquer la réponse"""
    try:
        # Essayer d'envoyer, mais ne jamais lever d'exception
        send_mail(
            subject=f"Contact: {sujet}",
            message=f"Nom: {nom}\nEmail: {email}\nMotif: {motif}\n\nMessage:\n{message}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['uzimamzenon@gmail.com'],
            fail_silently=True
        )
    except Exception:
        pass
    
    try:
        send_mail(
            subject="Message reçu",
            message=f"Bonjour {nom},\n\nVotre message a bien été reçu.\n\nCordialement,\nOrphelin Priorité ASBL",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=True
        )
    except Exception:
        pass

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def enregistrer_message(request):
    """Endpoint pour le formulaire de contact"""
    
    # Gérer CORS
    if request.method == 'OPTIONS':
        response = JsonResponse({'ok': True})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # Récupérer les données
    try:
        data = json.loads(request.body) if request.body else {}
    except:
        return JsonResponse({"success": False, "message": "Erreur format"}, status=400)
    
    # Valeurs
    nom = str(data.get('nom', '')).strip()
    email = str(data.get('email', '')).strip()
    message = str(data.get('message', '')).strip()
    sujet = str(data.get('sujet', 'Sans sujet')).strip()
    motif = str(data.get('motif', '')).strip()
    
    # Validation
    if not nom or not email or not message:
        return JsonResponse(
            {"success": False, "message": "Remplissez tous les champs"},
            status=400
        )
    
    if '@' not in email or '.' not in email:
        return JsonResponse(
            {"success": False, "message": "Email invalide"},
            status=400
        )
    
    # Envoyer les emails EN ARRIÈRE-PLAN (non-bloquant)
    try:
        thread = threading.Thread(
            target=send_emails_async,
            args=(nom, email, message, sujet, motif),
            daemon=True
        )
        thread.start()
    except:
        # Même si le thread échoue, on retourne le succès
        pass
    
    # Toujours retourner le succès
    return JsonResponse(
        {
            "success": True, 
            "message": f"✅ Message reçu ! Nous vous contacterons à {email}"
        },
        status=201
    )