from django.conf import settings
from django.db import models
from movies.models import Movie, Genre

class MovieDetail(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, primary_key=True)
    description = models.TextField()
    tagline = models.CharField(max_length=255, blank=True)

class UserRating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.FloatField()

    def __str__(self):
        return f"{self.rating}/10 by {self.user.username} for {self.movie.title}"

class UserPreference(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    genres = models.ManyToManyField(Genre, related_name='user_preferences')

    def __str__(self):
        return f"Preferences of {self.user.username}"