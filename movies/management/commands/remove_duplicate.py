from django.core.management.base import BaseCommand
from django.db import transaction
from movies.models import Movie
from django.db.models import Count

class Command(BaseCommand):
    help = 'Removes duplicate movies from the database'

    def handle(self, *args, **options):
        with transaction.atomic():  # Use a transaction to ensure atomicity
            # This query groups movies by `imdb_id`, `tmdb_id`, and `title`, and counts each group
            dupes = (
                Movie.objects.values('imdb_id', 'tmdb_id', 'title')
                .annotate(count_id=Count('id'))
                .filter(count_id__gt=1)
            )

            removed_count = 0

            # Loop through duplicates
            for dupe in dupes:
                # Fetch duplicate records, excluding the first one
                duplicate_movies = Movie.objects.filter(
                    imdb_id=dupe['imdb_id'],
                    tmdb_id=dupe['tmdb_id'],
                    title=dupe['title']
                ).order_by('id')[1:]  # Skip the first record

                count = duplicate_movies.count()
                duplicate_movies.delete()
                removed_count += count

                self.stdout.write(self.style.SUCCESS(f'Removed {count} duplicates of "{dupe["title"]}"'))

            self.stdout.write(self.style.SUCCESS(f'Total removed duplicates: {removed_count}'))
