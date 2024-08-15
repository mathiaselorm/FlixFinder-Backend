import pandas as pd
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie, Genre
from datetime import datetime

class Command(BaseCommand):
    help = 'Import movies from Kaggle dataset using pandas'

    def handle(self, *args, **options):
        self.import_movies()

    def import_movies(self):
        df = pd.read_csv(f'{settings.BASE_DIR}/data/movies_metadata.csv', encoding='utf-8')
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce', format='%Y-%m-%d')

        movies_created = 0
        for index, row in df.iterrows():
            try:
                # Handle genre creation or retrieval
                if pd.notna(row['genres']):
                    genre_data = json.loads(row['genres'].replace("'", '"'))  # Correctly parsing the JSON string
                    genre_objs = [Genre.objects.get_or_create(name=genre['name'])[0] for genre in genre_data]
                else:
                    genre_objs = []

                # Create or update the movie
                movie, created = Movie.objects.update_or_create(
                    imdb_id=row['imdb_id'],
                    defaults={
                        'title': row['title'],
                        'overview': row.get('overview', ''),
                        'release_date': row['release_date'] if pd.notna(row['release_date']) else None,
                        'cast': row.get('cast', ''),
                        'language': row.get('language', ''),
                        'average_rating': float(row['vote_average']) if pd.notna(row['vote_average']) else 0.0
                    }
                )
                
                # Add genres to the movie
                movie.genres.set(genre_objs)
                movies_created += 1 if created else 0

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error importing movie {row['title']}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {movies_created} movies'))
