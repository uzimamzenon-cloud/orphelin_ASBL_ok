from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crée un super utilisateur par défaut'

    def handle(self, *args, **options):
        # Vérifier si l'utilisateur admin existe déjà
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.SUCCESS('✅ Admin existe déjà'))
            return

        # Créer le super utilisateur
        User.objects.create_superuser(
            username='admin',
            email='admin@orphelin.com',
            password='Admin123456'
        )
        self.stdout.write(self.style.SUCCESS('✅ Super utilisateur créé: admin / Admin123456'))
