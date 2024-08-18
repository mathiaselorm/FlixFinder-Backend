from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from movies.models import Movie
from datetime import date


class Command(BaseCommand):
    help = 'Deletes movies with a release date of 2000 or earlier'

    def handle(self, *args, **options):
        # Set the cutoff date as January 1, 2001 (so it includes the year 2000)
        cutoff_date = date(2000, 1, 1)

        with transaction.atomic():
            # Query to find movies where the release date is on or before the cutoff date
            old_movies = Movie.objects.filter(release_date__lt=cutoff_date)
            count = old_movies.count()
            
            # Delete these movies
            old_movies.delete()

            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} movies released on or before the year 2000.'))


"""

class Command(BaseCommand):
    help = 'Deletes movies with any essential fields being empty'

    def handle(self, *args, **options):
        with transaction.atomic():  # Use a transaction to manage database integrity
            # Define a query to select movies where any of the essential fields is empty
            movies_to_delete = Movie.objects.filter(
                Q(imdb_id__isnull=True) | Q(imdb_id='') |
                Q(tmdb_id__isnull=True) |
                Q(title__isnull=True) | Q(title='') |
                Q(overview__isnull=True) | Q(overview='') |
                Q(release_date__isnull=True) |
                Q(cast__isnull=True) | Q(cast='') |
                Q(language__isnull=True) | Q(language='') |
                Q(poster_url__isnull=True) | Q(poster_url='') |
                Q(trailer_url__isnull=True) | Q(trailer_url='')
            )

            # Count the movies to be deleted
            count = movies_to_delete.count()

            # Perform the deletion
            movies_to_delete.delete()

            # Output the result
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} movies with essential fields missing'))
"""