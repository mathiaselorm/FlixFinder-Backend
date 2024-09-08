from celery import shared_task
from django.utils import timezone
from .models import Rating
from movies.models import Movie
from django.contrib.auth import get_user_model
import random
import logging


logger = logging.getLogger(__name__)



User = get_user_model()

@shared_task
def schedule_random_ratings(batch_size=100):
    users = User.objects.all()[:batch_size]  # Limit to a batch size of users
    movies = Movie.objects.all()[:batch_size]  # Limit to a batch size of movies
    ratings = []

    for user in users:
        # Randomly choose a subset of movies for each user to rate
        rated_movies = random.sample(list(movies), k=random.randint(1, min(10, len(movies))))
        for movie in rated_movies:
            score = round(random.uniform(1, 10), 1)  # Random score between 1 and 10
            rating = Rating(user=user, movie=movie, score=score, created_at=timezone.now())
            ratings.append(rating)
    
    # Bulk create ratings to optimize performance
    Rating.objects.bulk_create(ratings)
    return f"{len(ratings)} ratings have been added for {len(users)} users."



