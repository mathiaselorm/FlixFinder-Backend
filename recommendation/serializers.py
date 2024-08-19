from rest_framework import serializers
from accounts.serializers import UserSerializer
from movies.serializers import MovieSerializer 
from django.contrib.auth import get_user_model
from movies.models import Movie 
from .models import RecommendedMovie



User = get_user_model()


class RecommendedMovieSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = RecommendedMovie
        fields = ('id', 'user', 'movie', 'recommended_on')

    def create(self, validated_data):
        # Add custom creation logic if necessary, for example:
        user = self.context['request'].user
        movie_id = self.context['request'].data.get('movie_id')
        movie = Movie.objects.get(id=movie_id)
        recommended_movie, created = RecommendedMovie.objects.get_or_create(user=user, movie=movie)
        return recommended_movie