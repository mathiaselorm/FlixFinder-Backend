import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from movies.models import Movie  
from ratings.models import Rating  
from datetime import datetime
from faker import Faker
from django.conf import settings

User = get_user_model()

fake = Faker()

class Command(BaseCommand):
    help = 'Import ratings from a CSV file, creating fake users and validating movie IDs'

    def handle(self, *args, **options):
        # Construct the path to the CSV file
        file_path = os.path.join(settings.BASE_DIR, 'data', 'ratings.csv')

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                with transaction.atomic():
                    user_id = int(row['userId'])
                    movie_id = int(row['movieId'])
                    score = float(row['rating'])
                    timestamp = datetime.fromtimestamp(float(row['timestamp']))

                    user = self.get_or_create_user(user_id)
                    if user is None:
                        self.stdout.write(self.style.ERROR('Maximum retry limit reached for user creation. Skipping row.'))
                        continue

                    try:
                        movie = Movie.objects.get(id=movie_id)
                        rating, created = Rating.objects.update_or_create(
                            user=user,
                            movie=movie,
                            defaults={'score': score, 'created_at': timestamp, 'updated_at': timestamp}
                        )
                        action = "added" if created else "updated"
                        self.stdout.write(self.style.SUCCESS(f'Rating for {movie.title} by {user.email} {action}.'))
                    except Movie.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Skipped rating for movie ID {movie_id} as it does not exist.'))

    def get_or_create_user(self, user_id, retry=0):
        if retry > 3:  # Set a max retry limit to prevent infinite recursion
            return None
        try:
            email = fake.unique.email()
            return User.objects.get_or_create(
                id=user_id,
                defaults={
                    'email': email,
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'password': User.objects.make_random_password()
                }
            )[0]
        except IntegrityError:
            fake.unique.clear()
            return self.get_or_create_user(user_id, retry=retry + 1)





"""
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
"""