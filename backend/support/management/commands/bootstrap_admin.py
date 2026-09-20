import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create/update initial admin from environment variables.'
    def handle(self, *args, **kwargs):
        username=os.getenv('ADMIN_USERNAME','').strip(); password=os.getenv('ADMIN_PASSWORD','').strip(); email=os.getenv('ADMIN_EMAIL','').strip()
        if not username or not password:
            self.stdout.write('ADMIN_USERNAME/ADMIN_PASSWORD not set; skipping admin bootstrap.'); return
        user, created = User.objects.get_or_create(username=username, defaults={'email':email,'is_staff':True,'is_superuser':True})
        user.email=email or user.email; user.is_staff=True; user.is_superuser=True; user.set_password(password); user.save()
        profile=user.agent_profile; profile.role='admin'; profile.display_name=user.get_full_name() or username; profile.save()
        self.stdout.write(self.style.SUCCESS(f'Admin {username} ready.'))
