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

            # Validation des données obligatoires
            required_fields = ['nom', 'email', 'message']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                print(f"⚠️ Champs manquants : {missing_fields}")
                return JsonResponse(
                    {"success": False, "message": f"Champs obligatoires manquants : {', '.join(missing_fields)}"}, 
                    status=400
                )

            # 2. Envoi de l'Email au Gmail de l'ASBL
            email_sent = False
            try:
                print(f"📧 Configuration email : HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, USER={settings.EMAIL_HOST_USER}")
                
                sujet_email = f"📬 ASBL Contact : {data.get('sujet', 'Sans sujet')} ({data.get('nom')})"
                contenu_email = f"""
Nouveau message de contact :

👤 Nom : {data.get('nom')}
📧 Email : {data.get('email')}
🎯 Motif : {data.get('motif', 'Non spécifié')}
📝 Sujet : {data.get('sujet', 'Sans sujet')}

Message :
{data.get('message')}
                """
                
                # Envoyer à l'ASBL
                send_mail(
                    sujet_email,
                    contenu_email,
                    settings.EMAIL_HOST_USER,
                    ['uzimamzenon@gmail.com'], 
                    fail_silently=False,
                )
                print("✅ Email ASBL envoyé avec succès")
                email_sent = True
                
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
                print(f"⚠️ ERREUR EMAIL : {type(mail_err).__name__} - {mail_err}")
                import traceback
                traceback.print_exc()
                
                if email_sent:
                    # Si au moins l'email ASBL a été envoyé, continuer
                    return JsonResponse(
                        {"success": True, "message": "✅ Message reçu (confirmation email échouée)"}, 
                        status=201
                    )
                else:
                    # Si rien n'a été envoyé, erreur
                    return JsonResponse(
                        {"success": False, "message": f"Erreur email : {str(mail_err)}"}, 
                        status=500
                    )

            return JsonResponse(
                {"success": True, "message": "✅ Message enregistré et email envoyé !"}, 
                status=201
            )

        except json.JSONDecodeError as e:
            print(f"❌ ERREUR JSON : {e}")
            return JsonResponse(
                {"success": False, "message": "Format JSON invalide"}, 
                status=400
            )
        except Exception as e:
            print(f"❌ ERREUR GLOBALE : {type(e).__name__} - {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse(
                {"success": False, "message": f"Erreur serveur : {str(e)}"}, 
                status=500
            )
    
    return JsonResponse({"success": False, "message": "Méthode non autorisée"}, status=405)