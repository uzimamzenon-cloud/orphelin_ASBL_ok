from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crée un super utilisateur par défaut'

    def handle(self, *args, **options):
        # Vérifier si l'utilisateur admin existe déjà
        admin_user = User.objects.filter(username='admin').first()
        
        if admin_user:
            # L'admin existe, réinitialiser le mot de passe
            admin_user.set_password('Admin123456')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('✅ Admin réinitialisé: admin / Admin123456'))
            return

        # Créer le super utilisateur
        User.objects.create_superuser(
            username='admin',
            email='admin@orphelin.com',
            password='Admin123456'
        )
        self.stdout.write(self.style.SUCCESS('✅ Super utilisateur créé: admin / Admin123456'))
