import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Load Fuel Station Data"

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            with transaction.atomic():
                if not User.objects.filter(username='admin').exists():
                    User.objects.create_superuser(
                        username='admin',
                        email='admin@example.com',
                        password='admin123'
                    )
                    self.stdout.write(self.style.SUCCESS('Successfully created superuser'))
                else:
                    self.stdout.write(self.style.WARNING('Superuser already exists'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {str(e)}'))