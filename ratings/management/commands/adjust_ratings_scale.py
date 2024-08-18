from django.core.management.base import BaseCommand
from django.db import transaction
from ratings.models import Rating

class Command(BaseCommand):
    help = 'Adjust user ratings from a 0-5 scale to a 0-10 scale'

    def handle(self, *args, **options):
        with transaction.atomic():
            ratings = Rating.objects.all()
            updated_count = 0

            for rating in ratings:
                new_score = float(rating.score) * 2  # Ensure the operation happens in float
                rating.score = round(new_score, 1)  # Optionally round to 1 decimal place if needed
                rating.save()
                updated_count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully adjusted {updated_count} ratings to a 0-10 scale.'))
