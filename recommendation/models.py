from django.db import models
from django.contrib.auth import get_user_model
from movies.models import Movie

User = get_user_model()

class RecommendedMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommended_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='recommendations')
    recommended_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Recommended Movie'
        verbose_name_plural = 'Recommended Movies'
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.movie.title} recommended to {self.user.email} on {self.recommended_on}"
