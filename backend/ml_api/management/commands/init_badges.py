from django.core.management.base import BaseCommand
from ml_api.services.badge_service import initialize_badges


class Command(BaseCommand):
    help = 'Initialize all badges in the database'

    def handle(self, *args, **options):
        self.stdout.write('Initializing badges...')
        
        count = initialize_badges()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully initialized {count} badges!')
        )