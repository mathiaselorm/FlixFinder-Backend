from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from movies.models import Movie
from ratings.models import Rating
from movies.tmdb_client import TMDbClient
from django.conf import settings
import random
from decimal import Decimal, getcontext

User = get_user_model()

class Command(BaseCommand):
    help = 'Assign TMDB movie ratings to users based on TMDB ratings'

    def handle(self, *args, **options):
        client = TMDbClient(settings.TMDB_API_KEY)
        users = list(User.objects.all())
        movies = Movie.objects.all()
        total_ratings_assigned = 0
        errors = 0

        for movie in movies:
            self.stdout.write(f"Processing {movie.title} ({movie.tmdb_id})...")
            try:
                details = client.get_movie_details_by_tmdb_id(movie.tmdb_id)
                if details and 'vote_average' in details:
                    average_rating = Decimal(details['vote_average'])
                    with transaction.atomic():
                        num_users_to_rate = self.calculate_user_count_based_on_rating(average_rating)
                        num_ratings = self.create_ratings_for_movie(movie, average_rating, users, num_users_to_rate)
                        total_ratings_assigned += num_ratings
                        self.stdout.write(self.style.SUCCESS(f'Assigned ratings for {movie.title} from {num_ratings} users.'))
                else:
                    self.stdout.write(self.style.ERROR(f'No valid rating data found for {movie.title}'))
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f'Error processing {movie.title}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'Total ratings assigned: {total_ratings_assigned}'))
        if errors:
            self.stdout.write(self.style.ERROR(f'Total errors encountered: {errors}'))

    def calculate_user_count_based_on_rating(self, average_rating):
        # Apply different multipliers based on the average rating value
        multiplier = 3 if average_rating >= 5 else 2
        return max(int(average_rating * multiplier), 5)  # Ensure at least 5 users rate each movie

    def create_ratings_for_movie(self, movie, average_rating, users, num_users_to_rate):
        sampled_users = random.sample(users, min(len(users), num_users_to_rate))
        ratings_created = 0
        getcontext().prec = 2  # Set precision for Decimal operations

        for user in sampled_users:
            variation = Decimal(random.uniform(-0.5, 0.5))
            user_rating = average_rating + variation
            user_rating = max(min(user_rating, Decimal(10)), Decimal(0))  # Ensure rating is between 0 and 10

            Rating.objects.create(
                user=user,
                movie=movie,
                score=user_rating.quantize(Decimal('0.1'))  # Round to one decimal place
            )
            ratings_created += 1
        return ratings_created
