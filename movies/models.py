from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db.models import Avg


User = get_user_model()


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True, help_text="Enter a unique name for the genre.")
    tmdb_id = models.IntegerField(unique=True, db_index=True, null=True, help_text="The associated TMDB ID for the genre.")
    slug = models.SlugField(max_length=100, unique=True, db_index=True, blank=True, help_text="URL-friendly identifier automatically generated from the name.")
    
    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.name):
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Movie(models.Model):
    imdb_id = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True, help_text="IMDB identifier for the movie.")
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True, db_index=True, help_text="TMDB identifier for the movie.")
    title = models.CharField(max_length=255, db_index=True, help_text="The title of the movie.")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, blank=True, help_text="URL-friendly identifier automatically generated from the title.")
    overview = models.TextField(blank=True, null=True, help_text="Brief description of the movie.")
    release_date = models.DateField(db_index=True, blank=True, null=True, help_text="The release date of the movie.")
    cast = models.TextField(blank=True, null=True, help_text="List of main cast members.")
    language = models.CharField(max_length=100, blank=True, help_text="The primary language of the movie.")
    poster_url = models.URLField(blank=True, null=True, db_index=True, help_text="URL to the movie's poster image.")
    trailer_url = models.URLField(blank=True, null=True, help_text="URL to the movie's trailer.")
    genres = models.ManyToManyField(Genre, related_name='movies', help_text="Genres associated with this movie.")
    average_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0.0, help_text="Calculated average rating based on user reviews.")

    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.title):
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def update_average_rating(self):
        average = self.ratings.aggregate(average_score=Avg('score'))['average_score']
        self.average_rating = average if average is not None else 0.00
        self.save(update_fields=['average_rating'])

    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'Unknown Year'})"


class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name='comments', on_delete=models.CASCADE)
    comment = models.TextField(help_text="User's comment about the movie.")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.get_full_name()} on {self.movie.title}"



class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watchlisted_by')
    watched = models.BooleanField(default=False, help_text="Whether the user has watched the movie.")
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'movie'], name='unique_user_movie_watchlist')
        ]

    def __str__(self):
        return f"{self.user.first_name}'s watchlist"
