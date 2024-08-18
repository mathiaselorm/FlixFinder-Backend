from django.core.management.base import BaseCommand
from ratings.models import Rating
from django.db.models import Count
import numpy as np

class Command(BaseCommand):
    help = 'Limit the number of ratings per movie to the 95th percentile'

    def handle(self, *args, **options):
        # Calculate the 95th percentile of ratings count per movie
        rating_counts = Rating.objects.values('movie_id').annotate(count=Count('id'))
        counts = [count['count'] for count in rating_counts]
        cap = np.percentile(counts, 95)

        self.stdout.write(f"Capping ratings per movie at {int(cap)} ratings.")

        # Apply the cap
        for movie_id in Rating.objects.values_list('movie_id', flat=True).distinct():
            # Get ratings for the movie beyond the cap
            ratings_ids_to_remove = Rating.objects.filter(movie_id=movie_id).order_by('-id').values_list('id', flat=True)[int(cap):]
            count_removed = len(ratings_ids_to_remove)
            Rating.objects.filter(id__in=list(ratings_ids_to_remove)).delete()

            if count_removed > 0:
                self.stdout.write(f"Removed {count_removed} excess ratings from movie ID {movie_id}")

        self.stdout.write(self.style.SUCCESS('Successfully applied ratings cap to all movies.'))
