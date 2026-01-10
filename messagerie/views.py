import json
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

def page_accueil(request):
    return render(request, 'index.html')

@csrf_exempt
def enregistrer_message(request):
    if request.method == 'POST':
        try:
            # 1. On déballe les données JSON du JavaScript
            data = json.loads(request.body)
            print(f"✅ Données reçues : {data}") 

            # 2. Envoi de l'Email au Gmail de l'ASBL
            try:
                sujet_email = f"📬 ASBL Contact : {data.get('sujet')} ({data.get('nom')})"
                contenu_email = f"""
Nouveau message de contact :

👤 Nom : {data.get('nom')}
📧 Email : {data.get('email')}
🎯 Motif : {data.get('motif')}
📝 Sujet : {data.get('sujet')}

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
                print("✅ Email envoyé avec succès")
                
                # 3. Envoyer email de confirmation au visiteur
                send_mail(
                    f"✅ Merci {data.get('nom')} ! Votre message a été reçu",
                    f"""Bonjour {data.get('nom')},

Merci de nous avoir contactés. Votre message a bien été enregistré et nous vous répondrons au plus tôt.

Cordialement,
Orphelin Priorité ASBL""",
                    settings.EMAIL_HOST_USER,
                    [data.get('email')],
                    fail_silently=False,
                )
                print("✅ Email de confirmation envoyé au visiteur")
                
            except Exception as mail_err:
                print(f"⚠️ ERREUR EMAIL : {mail_err}")
                # Continuer même si l'email échoue

            return JsonResponse(
                {"success": True, "message": "✅ Message enregistré et email envoyé !"}, 
                status=201
            )

        except json.JSONDecodeError:
            print("❌ ERREUR : JSON invalide")
            return JsonResponse(
                {"success": False, "message": "Format JSON invalide"}, 
                status=400
            )
        except Exception as e:
            print(f"❌ ERREUR GLOBALE : {e}")
            return JsonResponse(
                {"success": False, "message": f"Erreur serveur : {str(e)}"}, 
                status=500
            )
    
    return JsonResponse({"success": False, "message": "Méthode non autorisée"}, status=405)