from django.core.management.base import BaseCommand
from django.db import transaction
from movies.models import Movie
from movies.tmdb_client import TMDbClient
from django.conf import settings
from django.core.paginator import Paginator

class Command(BaseCommand):
    help = 'Updates language, poster URL, and trailer URL of movies in the database from TMDB using IMDb ID'

    def handle(self, *args, **options):
        client = TMDbClient(settings.TMDB_API_KEY)
        paginator = Paginator(Movie.objects.exclude(imdb_id='').order_by('id'), 100)  # Processing 100 movies at a time
        updated_count = 0
        error_count = 0

        for page in range(1, paginator.num_pages + 1):
            for movie in paginator.page(page).object_list:
                self.stdout.write(f"Processing {movie.title} (IMDB ID: {movie.imdb_id})...")
                with transaction.atomic():
                    updated, error = self.update_movie_details(movie, client)
                    updated_count += updated
                    error_count += error

        self.stdout.write(self.style.SUCCESS(f'Successfully updated details for {updated_count} movies.'))
        if error_count:
            self.stdout.write(self.style.ERROR(f'Failed to update details for {error_count} movies.'))

    def update_movie_details(self, movie, client):
        try:
            details = client.get_movie_by_imdb_id(movie.imdb_id)  # Fetch using IMDb ID
            if details and details.get('movie_results'):
                movie_result = details['movie_results'][0] if details['movie_results'] else None
                if movie_result:
                    updates = []
                    if movie_result.get('original_language') and not movie.language:
                        movie.language = movie_result['original_language']
                        updates.append('language')

                    if movie_result.get('poster_path') and not movie.poster_url:
                        movie.poster_url = f'https://image.tmdb.org/t/p/w500{movie_result["poster_path"]}'
                        updates.append('poster_url')

                    trailer_url = self.extract_trailer_url(movie_result['id'], client)
                    if trailer_url and not movie.trailer_url:
                        movie.trailer_url = trailer_url
                        updates.append('trailer_url')

                    if updates:
                        movie.save(update_fields=updates)
                        self.stdout.write(self.style.SUCCESS(f'Updated {", ".join(updates)} for {movie.title}'))
                        return 1, 0  # 1 updated, 0 errors
            else:
                self.stdout.write("No relevant movie data returned from TMDB for IMDb ID.")
            return 0, 0  # No updates made
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating details for {movie.title}: {str(e)}'))
            return 0, 1  # 0 updated, 1 error

    def extract_trailer_url(self, tmdb_id, client):
        videos = client.get_movie_videos(tmdb_id)
        if videos and 'results' in videos:
            for video in videos['results']:
                if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                    return f'https://www.youtube.com/watch?v={video["key"]}'
        return None





