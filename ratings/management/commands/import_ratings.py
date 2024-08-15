from django.core.management.base import BaseCommand
import pandas as pd
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.db import transaction
from movies.models import Movie
from ratings.models import Rating
from django.conf import settings
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Import ratings from a dataset using pandas'

    def handle(self, *args, **options):
        self.import_ratings()

    def import_ratings(self):
        # Construct the file path using settings.BASE_DIR
        file_path = os.path.join(settings.BASE_DIR, 'data', 'ratings.csv')

        # Read the dataset
        data = pd.read_csv(file_path)

        successful_creates = 0
        failed_creates = 0

        # Process each row in the DataFrame
        for _, row in data.iterrows():
            try:
                with transaction.atomic():  # Use atomic transaction to ensure data integrity
                    # Fetch the user and movie instances based on ids provided in CSV
                    user = User.objects.get(pk=row['userId'])
                    movie = Movie.objects.get(pk=row['movieId'])

                    # Create a Rating instance
                    Rating.objects.create(
                        user=user,
                        movie=movie,
                        score=row['rating']
                    )

                successful_creates += 1

            except (User.DoesNotExist, Movie.DoesNotExist, IntegrityError) as e:
                # Handle cases where the user or movie isn't found, or other integrity issues
                self.stdout.write(self.style.ERROR(f'Failed to create rating for user {row["userId"]} and movie {row["movieId"]}: {str(e)}'))
                failed_creates += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully populated {successful_creates} ratings data'))
        if failed_creates:
            self.stdout.write(self.style.ERROR(f'Failed to create {failed_creates} ratings entries'))
