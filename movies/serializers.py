from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from .models import Movie, Genre, Comment, Watchlist
from django.urls import reverse

class GenreMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug']

class MovieMinimalSerializer(serializers.ModelSerializer):
    genres = GenreMinimalSerializer(many=True, read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'slug', 'title', 'overview', 'language', 'release_date', 'poster_url', 'trailer_url', 'genres', 'average_rating', 'url']

    def get_url(self, obj):
        request = self.context.get('request')
        genre_slug = obj.genres.first().slug if obj.genres.exists() else None
        if genre_slug:
            url = reverse('movie-detail', kwargs={'genre_slug': genre_slug, 'identifier': obj.slug})
            return request.build_absolute_uri(url) 


class PaginatedMovieSerializer(serializers.Serializer):
    """
    Serializer for paginating movies.
    """
    movies = MovieMinimalSerializer(many=True, read_only=True)
    count = serializers.IntegerField(read_only=True)
    next = serializers.URLField(read_only=True)
    previous = serializers.URLField(read_only=True)
    
    
class GenreSerializer(serializers.ModelSerializer):
    movies = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ['id', 'slug', 'name', 'movies']

    def get_movies(self, obj):
        """
        Manually paginate the movies queryset.
        """
        # Get movies related to the genre
        movies = obj.movies.all()
        # Set up pagination
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(movies, self.context['request'], view=self.context['view'])

        # Serialize page of movies
        serializer = MovieMinimalSerializer(page, many=True, context={'request': self.context['request']})
        return {
            'movies': serializer.data,
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link()
        }
        
        
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'movie', 'comment', 'timestamp']
        read_only_fields = ['user', 'timestamp']


class PaginatedCommentSerializer(serializers.Serializer):
    """
    Serializer for paginating comments.
    """
    comments = CommentSerializer(many=True, read_only=True)
    count = serializers.IntegerField(read_only=True)
    next = serializers.URLField(read_only=True)
    previous = serializers.URLField(read_only=True)
    
    
class MovieSerializer(serializers.ModelSerializer):
    genres = GenreMinimalSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    average_rating = serializers.DecimalField(max_digits=4, decimal_places=2, read_only=True)

    class Meta:
        model = Movie
        fields = [
            'id', 'slug', 'title', 'overview', 'release_date', 'cast',
            'language', 'poster_url', 'trailer_url', 'genres',
            'average_rating', 'comments'
        ]

    def get_comments(self, obj):
        """
        Custom method to paginate comments within the movie serializer.
        """
        comments = obj.comments.all()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(comments, self.context['request'])

        serializer = CommentSerializer(page, many=True, context={'request': self.context['request']})
        return {
            'comments': serializer.data,
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link()
        }
        

class WatchlistSerializer(serializers.ModelSerializer):
    movie_title = serializers.ReadOnlyField(source='movie.title')
    user = serializers.ReadOnlyField(source='user.first_name')  
    
    class Meta:
        model = Watchlist
        fields = ['id', 'user', 'movie', 'movie_title', 'watched', 'added_on']
        read_only_fields = ['id', 'added_on', 'user']  
