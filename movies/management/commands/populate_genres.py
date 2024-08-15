from django.core.management.base import BaseCommand
from movies.models import Genre
from movies.tmdb_client import TMDbClient
from django.conf import settings

class Command(BaseCommand):
    help = 'Populates the database with genres from TMDb'

    def handle(self, *args, **options):
        client = TMDbClient(settings.TMDB_API_KEY)
        genre_data = client.get_genres()
        if genre_data:
            for genre in genre_data.get('genres', []):
                Genre.objects.get_or_create(name=genre['name'], defaults={'tmdb_id': genre['id']})
            self.stdout.write(self.style.SUCCESS('Successfully populated genres'))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch genres'))
