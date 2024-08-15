from django.core.management.base import BaseCommand
from ratings.models import Rating

class Command(BaseCommand):
    help = 'Delete all ratings from the database'

    def handle(self, *args, **options):
        count = Rating.objects.count()
        Rating.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} ratings.'))
