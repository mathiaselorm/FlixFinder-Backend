from django.core.management.base import BaseCommand
from movies.models import Movie, Genre

class Command(BaseCommand):
    help = 'Assigns a generic genre to movies without specific genre information'

    def handle(self, *args, **options):
        # Ensure the generic genre exists in the database
        generic_genre, created = Genre.objects.get_or_create(name='Unknown')
        
        # Query for all movies that do not have any genres associated
        movies_without_genres = Movie.objects.filter(genres__isnull=True)
        
        # Assign the generic genre to these movies
        for movie in movies_without_genres:
            movie.genres.add(generic_genre)
            movie.save()
            self.stdout.write(self.style.SUCCESS(f'Assigned generic genre to {movie.title}'))

        self.stdout.write(self.style.SUCCESS(f'Total movies updated: {movies_without_genres.count()}'))



"""
from django.core.management.base import BaseCommand
from django.db import transaction
from movies.models import Movie, Genre
from movies.tmdb_client import TMDbClient
from django.conf import settings
from django.core.paginator import Paginator

class Command(BaseCommand):
    help = 'Populates missing genre information for movies from TMDB using IMDb IDs'

    def handle(self, *args, **options):
        client = TMDbClient(settings.TMDB_API_KEY)
        # Processing movies that are missing genre information
        paginator = Paginator(Movie.objects.filter(genres__isnull=True).exclude(imdb_id='').order_by('id'), 100) 
        updated_count = 0
        error_count = 0

        for page in range(1, paginator.num_pages + 1):
            for movie in paginator.page(page).object_list:
                self.stdout.write(f"Processing {movie.title} (IMDB ID: {movie.imdb_id})...")
                with transaction.atomic():
                    if self.update_movie_genres(movie, client):
                        updated_count += 1
                    else:
                        error_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully populated genres for {updated_count} movies.'))
        if error_count:
            self.stdout.write(self.style.ERROR(f'Failed to populate genres for {error_count} movies.'))

    def update_movie_genres(self, movie, client):
        try:
            details = client.get_movie_by_imdb_id(movie.imdb_id)  # Fetch using IMDb ID
            if details and 'movie_results' in details and details['movie_results']:
                movie_result = details['movie_results'][0]
                if 'genres' in movie_result and movie_result['genres']:
                    for genre_info in movie_result['genres']:
                        genre, created = Genre.objects.get_or_create(name=genre_info['name'])
                        movie.genres.add(genre)
                    movie.save()
                    self.stdout.write(self.style.SUCCESS(f'Genres updated for {movie.title}'))
                    return True
                else:
                    self.stdout.write(self.style.WARNING(f'No genres found in TMDB for {movie.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'No movie results returned from TMDB for {movie.imdb_id}'))
            return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating genres for {movie.title}: {str(e)}'))
            return False
"""