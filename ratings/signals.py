from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Rating



@receiver(post_save, sender=Rating)
def update_movie_rating_on_save(sender, instance, **kwargs):
    """
    Update the movie's average rating whenever a rating is added or updated.
    """
    instance.movie.update_average_rating()
    

@receiver(post_delete, sender=Rating)
def update_movie_rating_on_delete(sender, instance, **kwargs):
    """
    Update the movie's average rating whenever a rating is deleted.
    """
    if instance.movie:
        instance.movie.update_average_rating()
