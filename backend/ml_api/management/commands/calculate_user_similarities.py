from django.core.management.base import BaseCommand
from ml_api.services.user_similarity_service import get_user_similarity_service
from ml_api.models import User, UserSimilarity


class Command(BaseCommand):
    help = 'Calculate user similarities for collaborative filtering'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Calculate similarities for all users',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Calculate similarities for specific username',
        )
    
    def handle(self, *args, **options):
        service = get_user_similarity_service()
        
        if options['all']:
            self.stdout.write("Calculating similarities for ALL users...")
            total = service.calculate_all_similarities()
            self.stdout.write(
                self.style.SUCCESS(f"Created {total} similarity records")
            )
        
        elif options['user']:
            username = options['user']
            try:
                user = User.objects.get(username=username)
                self.stdout.write(f"Calculating for: {username}")
                count = service.calculate_similarities_for_user(user)
                self.stdout.write(
                    self.style.SUCCESS(f"Created {count} similarities")
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"User '{username}' not found")
                )
        else:
            self.stdout.write(
                self.style.WARNING("Use --all or --user USERNAME")
            )