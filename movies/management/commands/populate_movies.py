from django.core.management.base import BaseCommand
from django.db import transaction
from movies.models import Movie, Genre
from movies.tmdb_client import TMDbClient
from django.conf import settings
from datetime import datetime

class Command(BaseCommand):
    help = 'Populates or updates the database with movies from TMDB starting from page 200'
    
    def parse_date(self, date_str):
        """Parses a date string in YYYY-MM-DD format, returning None if invalid."""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None

    def handle(self, *args, **options):
        client = TMDbClient(settings.TMDB_API_KEY)
        all_genres = Genre.objects.all()
        genre_dict = {genre.name: genre for genre in all_genres}

        start_page = 45
        max_pages = 100

        for page in range(start_page, max_pages + 1):
            self.stdout.write(f"Processing movies from TMDB page {page}...")
            movie_data = client.get_movies(page=page)
            if not movie_data or not movie_data.get('results'):
                self.stdout.write(self.style.ERROR('No more data available or failed to fetch data'))
                break

            with transaction.atomic():
                for tmdb_movie in movie_data.get('results', []):
                    imdb_id = self.fetch_imdb_id_from_tmdb_movie(tmdb_movie, client)
                    if not imdb_id:
                        continue  # Skip movies without a valid imdb_id

                    movie_obj, created = Movie.objects.update_or_create(
                        imdb_id=imdb_id,
                        defaults={
                            'title': tmdb_movie['title'],
                            'overview': tmdb_movie.get('overview', ''),
                            'release_date': self.parse_date(tmdb_movie.get('release_date')),
                            'language': tmdb_movie.get('original_language'),
                            'poster_url': f"https://image.tmdb.org/t/p/w500{tmdb_movie['poster_path']}" if tmdb_movie.get('poster_path') else None,
                            'average_rating': tmdb_movie.get('vote_average', 0.0)
                        }
                    )
                    self._assign_movie_details(movie_obj, tmdb_movie, genre_dict, client)

            self.stdout.write(self.style.SUCCESS(f'Successfully populated or updated movies from page {page}'))

    def fetch_imdb_id_from_tmdb_movie(self, tmdb_movie, client):
        details = client.get_movie_details_by_tmdb_id(tmdb_movie['id'])
        return details.get('imdb_id') if details else None

    def _assign_movie_details(self, movie_obj, tmdb_movie, genre_dict, client):
        tmdb_id = tmdb_movie.get('id')

        # Update trailer URL
        videos = client.get_movie_videos(tmdb_id)
        trailers = [video for video in videos.get('results', []) if video['type'] == 'Trailer']
        if trailers:
            movie_obj.trailer_url = f"https://www.youtube.com/watch?v={trailers[0]['key']}"
            movie_obj.save(update_fields=['trailer_url'])

        # Update genres using genre IDs to names mapping
        tmdb_genre_ids = set(tmdb_movie.get('genre_ids', []))
        for tmdb_genre_id in tmdb_genre_ids:
            genre_name = self.fetch_genre_name_from_tmdb_genre_id(tmdb_genre_id, client)
            if genre_name in genre_dict:
                movie_obj.genres.add(genre_dict[genre_name])
            else:
                new_genre, _ = Genre.objects.get_or_create(name=genre_name)
                movie_obj.genres.add(new_genre)

    def fetch_genre_name_from_tmdb_genre_id(self, tmdb_genre_id, client):
        genre_data = client.get_genres()
        for genre in genre_data.get('genres', []):
            if genre['id'] == tmdb_genre_id:
                return genre['name']
        return None
