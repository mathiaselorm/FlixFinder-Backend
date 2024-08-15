from django.core.management.base import BaseCommand
from django.db import transaction
from movies.models import Movie
from movies.tmdb_client import TMDbClient
from django.conf import settings
from django.core.paginator import Paginator

class Command(BaseCommand):
    help = 'Updates the average ratings of movies in the database from TMDB'

    def handle(self, *args, **options):
        client = TMDbClient(settings.TMDB_API_KEY)
        paginator = Paginator(Movie.objects.all(), 100)  # Processing 100 movies at a time
        updated_count = 0
        error_count = 0

        for page in range(1, paginator.num_pages + 1):
            for movie in paginator.page(page).object_list:
                if not movie.tmdb_id:
                    continue  # Skip movies without a TMDB ID
                self.stdout.write(f"Processing {movie.title} ({movie.tmdb_id})...")
                with transaction.atomic():
                    updated, error = self.update_movie_banner(movie, client)
                    updated_count += updated
                    error_count += error

        self.stdout.write(self.style.SUCCESS(f'Successfully updated banner URLs for {updated_count} movies.'))
        if error_count:
            self.stdout.write(self.style.ERROR(f'Failed to update banner URLs for {error_count} movies.'))

    def update_movie_banner(self, movie, client):
        try:
            images = client.get_movie_images_by_tmdb_id(movie.tmdb_id)
            if images and 'backdrops' in images and images['backdrops']:
                # Choose the first backdrop as the banner
                banner_path = images['backdrops'][0]['file_path']
                movie.banner_url = f'https://image.tmdb.org/t/p/w780{banner_path}'
                movie.save(update_fields=['banner_url'])
                self.stdout.write(self.style.SUCCESS(f'Updated banner URL for {movie.title}: {movie.banner_url}'))
                return 1, 0  # 1 updated, 0 errors
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating banner URL for {movie.title}: {str(e)}'))
        return 0, 1  # 0 updated, 1 error


"""
        for page in range(1, paginator.num_pages + 1):
            for movie in paginator.page(page).object_list:
                if not movie.tmdb_id:
                    continue  # Skip movies without a TMDB ID
                self.stdout.write(f"Processing {movie.title} ({movie.tmdb_id})...")
                with transaction.atomic():
                    updated, error = self.update_movie_rating(movie, client)
                    updated_count += updated
                    error_count += error

        self.stdout.write(self.style.SUCCESS(f'Successfully updated ratings for {updated_count} movies.'))
        if error_count:
            self.stdout.write(self.style.ERROR(f'Failed to update ratings for {error_count} movies.'))

    def update_movie_rating(self, movie, client):
        try:
            details = client.get_movie_details_by_tmdb_id(movie.tmdb_id)
            if details and 'vote_average' in details:
                movie.average_rating = details['vote_average']
                movie.save(update_fields=['average_rating'])
                self.stdout.write(self.style.SUCCESS(f'Updated average rating for {movie.title}: {details["vote_average"]}'))
                return 1, 0  # 1 updated, 0 errors
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating {movie.title}: {str(e)}'))
        return 0, 1  # 0 updated, 1 error
"""