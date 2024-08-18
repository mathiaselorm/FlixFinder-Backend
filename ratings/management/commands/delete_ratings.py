from django.core.management.base import BaseCommand
from ratings.models import Rating
from movies.models import Movie
from django.contrib.auth import get_user_model


User = get_user_model()

class Command(BaseCommand):
    help = 'Check if all user IDs and movie IDs in ratings are present in the user and movie datasets'

    def handle(self, *args, **options):
        ratings = Rating.objects.all().select_related('user', 'movie')
        missing_users = 0
        missing_movies = 0
        total_ratings = ratings.count()

        for rating in ratings:
            if not User.objects.filter(id=rating.user_id).exists():
                missing_users += 1
                self.stdout.write(self.style.ERROR(f'Missing User ID: {rating.user_id} in Rating ID: {rating.id}'))
            if not Movie.objects.filter(id=rating.movie_id).exists():
                missing_movies += 1
                self.stdout.write(self.style.ERROR(f'Missing Movie ID: {rating.movie_id} in Rating ID: {rating.id}'))

        self.stdout.write(self.style.SUCCESS(f'Total ratings checked: {total_ratings}'))
        self.stdout.write(self.style.SUCCESS(f'Missing user records: {missing_users}'))
        self.stdout.write(self.style.SUCCESS(f'Missing movie records: {missing_movies}'))

        if missing_users == 0 and missing_movies == 0:
            self.stdout.write(self.style.SUCCESS('All user and movie IDs in ratings are correctly matched with the user and movie datasets.'))
        else:
            self.stdout.write(self.style.ERROR('There are discrepancies in the dataset IDs.'))








"""
from django.core.management.base import BaseCommand
from ratings.models import Rating

class Command(BaseCommand):
    help = 'Delete all ratings from the database'

    def handle(self, *args, **options):
        count = Rating.objects.count()
        Rating.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} ratings.'))
"""