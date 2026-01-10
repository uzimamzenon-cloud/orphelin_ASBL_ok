import json
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage  # Changé ici : le bon nom de modèle
from django.views.decorators.csrf import csrf_exempt

def page_accueil(request):
    return render(request, 'index.html')

@csrf_exempt
def enregistrer_message(request):
    if request.method == 'POST':
        try:
            # 1. On déballe le cadeau JSON reçu du JavaScript
            data = json.loads(request.body)
            print(f"--- Données reçues : {data}") 

            # 2. Stockage dans la Base de Données
            # On adapte les noms pour correspondre exactement à models.py
            nouveau_msg = ContactMessage.objects.create(
                name=data.get('nom'),      # JS 'nom' -> DB 'name'
                email=data.get('email'),   # JS 'email' -> DB 'email'
                subject=data.get('sujet'), # JS 'sujet' -> DB 'subject'
                reason=data.get('motif'),  # JS 'motif' -> DB 'reason'
                message=data.get('message')
            )
            print(f"--- OK : Enregistré avec ID {nouveau_msg.id}")

            # 3. Envoi de l'Email au Gmail de l'ASBL
            try:
                sujet_email = f"ASBL Contact : {data.get('sujet')} ({data.get('nom')})"
                contenu_email = f"""
                Nouveau message de : {data.get('nom')}
                Email : {data.get('email')}
                Motif : {data.get('motif')}
                
                Message :
                {data.get('message')}
                """
                
                send_mail(
                    sujet_email,
                    contenu_email,
                    settings.EMAIL_HOST_USER,
                    ['uzimamzenon@gmail.com'], 
                    fail_silently=False,
                )
                print("--- OK : Email envoyé.")
            except Exception as mail_err:
                print(f"--- ERREUR MAIL : {mail_err}")

            return JsonResponse({"message": "Succès ! Information stockée et Email envoyé !"}, status=201)

        except Exception as e:
            print(f"--- ERREUR GLOBALE : {e}")
            return JsonResponse({"message": f"Défaut de stockage : {str(e)}"}, status=400)
    
    return JsonResponse({"message": "Accès refusé"}, status=405)