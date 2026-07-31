from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Create admin user if not exists'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME', 'admin')
        email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        password = os.getenv('ADMIN_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING('ADMIN_PASSWORD not set, using default "admin123"'))
            password = 'admin123'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'✅ Admin user "{username}" created successfully!'))
            self.stdout.write(self.style.SUCCESS(f'📧 Email: {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'ℹ️ Admin user "{username}" already exists'))