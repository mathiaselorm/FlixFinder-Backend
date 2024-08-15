
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Movie, Genre, Comment, Watchlist
from .serializers import MovieSerializer, GenreSerializer, CommentSerializer, MovieMinimalSerializer, GenreMinimalSerializer, WatchlistSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from . utils import get_object_by_id_or_slug




class GenreListView(APIView):
    """
    Retrieves a list of all genres available in the database.
    This endpoint is public and does not require authentication.
    
    Responses:
    200: Success - Returns a list of all genres.
    500: Internal Server Error - When there is a problem with the server or the database.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={
            200: GenreMinimalSerializer(many=True),
            500: 'Internal Server Error'
        },
        operation_description="Retrieve a list of all genres."
    )
    def get(self, request, format=None):
        try:
            genres = Genre.objects.all()
            serializer = GenreMinimalSerializer(genres, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Internal server error", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GenreCreateView(APIView):
    """
    Creates a new genre in the database.
    Access to this endpoint is restricted to admin users only.

    Responses:
    201: Created - Returns the created genre data.
    400: Bad Request - When the data provided is invalid.
    """
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        request_body=GenreMinimalSerializer,
        responses={
            201: GenreMinimalSerializer(),
            400: 'Bad Request'
        },
        operation_description="Create a new genre."
    )
    def post(self, request, format=None):
        serializer = GenreMinimalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GenreDetailView(APIView):
    """
    Retrieves a detailed view of a genre by its slug or ID.
    This endpoint is publicly accessible.

    Responses:
    200: Success - Returns detailed genre data.
    404: Not Found - When the genre with the specified identifier does not exist.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={
            200: GenreSerializer(),
            404: 'Not Found'
        },
        operation_description="Retrieve details of a specific genre."
    )
    def get(self, request, identifier, format=None):
        genre = get_object_by_id_or_slug(Genre, identifier, slug_field='slug')
        if genre:
            serializer = GenreSerializer(genre, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Genre not found"}, status=status.HTTP_404_NOT_FOUND)
        

class GenreUpdateDeleteView(APIView):
    """
    Updates or deletes a genre based on the provided identifier.

    PUT: Updates the specified genre with provided data.
    DELETE: Deletes the specified genre.
    """
    permission_classes = [permissions.IsAuthenticated]  # Update to restrict to authenticated users

    @swagger_auto_schema(
        request_body=GenreSerializer,
        responses={
            200: GenreSerializer(),
            400: 'Bad Request',
            404: 'Not Found'
        },
        operation_description="Update an existing genre."
    )
    def put(self, request, identifier, format=None):
        genre = get_object_by_id_or_slug(Genre, identifier, slug_field='slug')
        if not genre:
            return Response({"error": "Genre not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GenreSerializer(genre, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={
            204: 'No Content',
            404: 'Not Found'
        },
        operation_description="Delete a specific genre."
    )
    def delete(self, request, identifier, format=None):
        genre = get_object_by_id_or_slug(Genre, identifier, slug_field='slug')
        if not genre:
            return Response({"error": "Genre not found"}, status=status.HTTP_404_NOT_FOUND)

        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class GenreMoviesListView(generics.ListAPIView):
    """
    Retrieves a list of movies associated with a specific genre, identified by the genre's slug.
    """
    serializer_class = MovieMinimalSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['title', 'release_date', 'genres__name', 'language']
    ordering_fields = ['title', 'release_date']
    ordering = ['title']
    search_fields = ['title', 'genres__name', 'cast']

    @swagger_auto_schema(
        operation_description="Retrieve a list of movies within a specified genre.",
        manual_parameters=[
            openapi.Parameter(
                'genre_slug',
                openapi.IN_PATH,
                description="Slug of the genre to filter movies by",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: MovieMinimalSerializer(many=True, help_text="Returns a list of movies associated with the specified genre."),
            404: "Genre not found"
        },
        tags=['Movies by Genre']
    )
    def get_queryset(self):
        """
        Fetches movies that belong to a specific genre identified by 'genre_slug'.
        If the genre does not exist, it raises a 404 error.
        """
        genre = get_object_by_id_or_slug(Genre, self.kwargs['genre_slug'], slug_field='slug')
        if not genre:
            raise NotFound(detail="Genre not found")
        return genre.movies.all()

    def list(self, request, *args, **kwargs):
        """
        Overrides the list method to apply custom filtering and return a response.
        Utilizes the serializer to format the movie data correctly before sending the response.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class MovieDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific movie within a genre.",
        manual_parameters=[
            openapi.Parameter(
                'genre_slug',
                openapi.IN_PATH,
                description="Slug of the genre to which the movie belongs",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'identifier',
                openapi.IN_PATH,
                description="Identifier or slug of the movie",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: MovieSerializer(help_text="Returns detailed information about the movie."),
            404: "Movie not found in the specified genre"
        },
        tags=['Movie Details']
    )
    def get(self, request, genre_slug, identifier):
        """
        Retrieves detailed information about a movie specified by its identifier or slug within a given genre.
        Ensures that the movie is associated with the specified genre before returning its details.
        If the movie is not found under the specified genre, it returns a 404 error.
        """
        try:
            genre = get_object_by_id_or_slug(Genre, genre_slug, slug_field='slug')
            movie = get_object_by_id_or_slug(Movie, identifier, slug_field='slug')
        except NotFound as e:
            return Response({'error': str(e)}, status=HTTP_404_NOT_FOUND)

        if not movie.genres.filter(slug=genre_slug).exists():
            return Response({"error": "Movie not found in the specified genre"}, status=HTTP_404_NOT_FOUND)

        serializer = MovieSerializer(movie, context={'request': request})
        return Response(serializer.data)


class MovieUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Update details of a specific movie within a genre.",
        request_body=MovieSerializer,
        responses={
            200: MovieSerializer(help_text="Returns the updated movie information."),
            400: 'Validation errors',
            404: "Movie not found in the specified genre"
        },
        manual_parameters=[
            openapi.Parameter('genre_slug', openapi.IN_PATH, description="Slug of the genre", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('identifier', openapi.IN_PATH, description="Identifier or slug of the movie", type=openapi.TYPE_STRING, required=True)
        ],
        tags=['Movie Update']
    )
    def put(self, request, genre_slug, identifier):
        """
        Updates a movie specified by its identifier or slug within a given genre based on the provided data.
        Validates the existence of the movie within the specified genre before attempting an update.
        If the movie is not found under the specified genre or validation fails, appropriate error messages and status codes are returned.
        """
        try:
            genre = get_object_by_id_or_slug(Genre, slug=genre_slug)
            movie = get_object_by_id_or_slug(Movie, identifier, slug_field='slug')
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        if not movie.genres.filter(slug=genre_slug).exists():
            return Response({"error": "Movie not found in the specified genre"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MovieSerializer(movie, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class MovieDeleteView(APIView):
    """
    Delete a movie from a specific genre by its slug.

    This view allows users to delete a movie identified by its slug within a specified genre.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Delete a specific movie from a genre.",
        responses={
            204: openapi.Response(description="No Content. Movie deleted successfully."),
            404: openapi.Response(description="Not Found. Movie not found in the specified genre."),
        }
    )
    def delete(self, request, genre_slug, identifier):
        try:
            # Retrieve the genre
            genre = get_object_by_id_or_slug(Genre, genre_slug, slug_field='slug')
            # Retrieve the movie within the genre
            movie = get_object_by_id_or_slug(Movie, identifier, slug_field='slug')
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the movie is part of the specified genre
        if movie.genres.filter(slug=genre_slug).exists():
            movie.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Movie not found in the specified genre"}, status=status.HTTP_404_NOT_FOUND)


    
    
class MovieCommentsView(generics.ListCreateAPIView):
    """
    View to list all comments for a specific movie within a genre and create new comments.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all comments for a specific movie within a specified genre.",
        responses={
            200: CommentSerializer(many=True),
            404: 'Movie or Genre not found'
        }
    )
    def get_queryset(self):
        """
        Return a list of all comments for the movie specified by the genre_slug and identifier.
        """
        # Ensure the movie is part of the specified genre
        genre = get_object_or_404(Genre, slug=self.kwargs['genre_slug'])
        movie = get_object_or_404(Movie, slug=self.kwargs['identifier'], genres=genre)
        return Comment.objects.filter(movie=movie)

    @swagger_auto_schema(
        operation_description="Create a new comment for a specific movie within a specified genre.",
        responses={
            201: CommentSerializer(),
            400: 'Bad Request - Invalid data'
        }
    )
    def perform_create(self, serializer):
        """
        Create a new comment, associating it with the correct movie and the current user.
        """
        genre = get_object_or_404(Genre, slug=self.kwargs['genre_slug'])
        movie = get_object_or_404(Movie, slug=self.kwargs['identifier'], genres=genre)
        serializer.save(user=self.request.user, movie=movie)
        
        

class CommentUpdateView(generics.RetrieveUpdateAPIView):
    """
    View to retrieve and update a user's comment.
    Only the owner of the comment is allowed to update it.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return comments only for the currently authenticated user.
        """
        user = self.request.user
        return Comment.objects.filter(user=user)

    def get_object(self):
        """
        Override the standard `get_object` method to ensure users can only access their own comments.
        Raises PermissionDenied if the comment does not belong to the user.
        """
        comment = super().get_object()
        if comment.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this comment.")
        return comment

    @swagger_auto_schema(
        operation_description="Retrieve and update a user's comment.",
        responses={
            200: CommentSerializer(),
            403: "Permission denied - You do not have permission to edit this comment.",
            404: "Comment not found",
            400: "Bad Request - Invalid data"
        }
    )
    def put(self, request, *args, **kwargs):
        """
        Handle the PUT request to update a comment.
        Returns the updated comment if the request is successful.
        """
        return super().put(request, *args, **kwargs)
    
    
class CommentDeleteView(generics.DestroyAPIView):
    """
    View to delete a user's comment.
    Only the owner of the comment is allowed to delete it.
    """
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return comments only for the currently authenticated user.
        """
        user = self.request.user
        return Comment.objects.filter(user=user)

    def get_object(self):
        """
        Ensure users can only delete their own comments.
        Raises PermissionDenied if the comment does not belong to the user.
        """
        comment = super().get_object()
        if comment.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this comment.")
        return comment

    @swagger_auto_schema(
        operation_description="Delete a user's comment.",
        responses={
            204: "Comment successfully deleted.",
            403: "Permission denied - You do not have permission to delete this comment.",
            404: "Comment not found"
        }
    )
    def delete(self, request, *args, **kwargs):
        """
        Handle the DELETE request to delete a comment.
        Returns a 204 status if the deletion is successful.
        """
        return super().delete(request, *args, **kwargs)
    
    
class TopRatedMoviesView(APIView):
    """
    View to list all top-rated movies based on a dynamic average rating threshold.
    Allows querying for top-rated movies above a specific average rating.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        # Default threshold for top-rated movies is 8.0, can be overridden by query parameter
        threshold = request.query_params.get('threshold', 8.0)
        try:
            threshold = float(threshold)
        except ValueError:
            return Response({"error": "Invalid threshold value."}, status=status.HTTP_400_BAD_REQUEST)

        top_rated_movies = Movie.objects.filter(average_rating__gte=threshold)
        # Pass the request context to the serializer
        serializer = MovieMinimalSerializer(top_rated_movies, many=True, context={'request': request})
        return Response(serializer.data)

    

class WatchlistCreateView(APIView):
    """
    API view to create a new watchlist entry. 
    Only authenticated users can create a watchlist entry.
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new watchlist entry for the authenticated user.",
        request_body=WatchlistSerializer,
        responses={
            201: WatchlistSerializer,
            400: "Bad Request - Invalid data provided.",
            401: "Unauthorized - User is not authenticated."
        }
    )
    def post(self, request, format=None):
        """
        Handle the POST request to create a watchlist entry.
        Links the watchlist item to the currently authenticated user.
        """
        serializer = WatchlistSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class WatchlistListView(APIView):
    """
    API view to list all watchlist entries for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all watchlist entries for the authenticated user.",
        responses={
            200: WatchlistSerializer(many=True),
            401: "Unauthorized - User is not authenticated."
        }
    )
    def get(self, request, format=None):
        """
        Handle the GET request to list watchlist entries.
        Filters watchlist items by the authenticated user.
        """
        watchlist_items = Watchlist.objects.filter(user=request.user)
        serializer = WatchlistSerializer(watchlist_items, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class WatchlistUpdateView(APIView):
    """
    API view to retrieve and update a watchlist entry.
    Only the authenticated user who owns the watchlist entry can update it.
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a specific watchlist entry by ID.",
        responses={
            200: WatchlistSerializer(),
            404: "Not Found - Watchlist entry not found.",
            401: "Unauthorized - User is not authenticated."
        }
    )
    def get(self, request, pk, format=None):
        """
        Handle GET request to retrieve a specific watchlist entry.
        """
        watchlist_item = get_object_or_404(Watchlist, pk=pk, user=request.user)
        serializer = WatchlistSerializer(watchlist_item, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a specific watchlist entry by ID.",
        request_body=WatchlistSerializer,
        responses={
            200: WatchlistSerializer(),
            400: "Bad Request - Invalid data.",
            404: "Not Found - Watchlist entry not found.",
            401: "Unauthorized - User is not authenticated."
        }
    )
    def put(self, request, pk, format=None):
        """
        Handle PUT request to update a specific watchlist entry.
        """
        watchlist_item = get_object_or_404(Watchlist, pk=pk, user=request.user)
        serializer = WatchlistSerializer(watchlist_item, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class WatchlistDeleteView(APIView):
    """
    API view to delete a watchlist entry.
    Only the authenticated user who owns the watchlist entry can delete it.
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Delete a specific watchlist entry by ID.",
        responses={
            204: "No Content - Watchlist entry deleted successfully.",
            404: "Not Found - Watchlist entry not found.",
            401: "Unauthorized - User is not authenticated."
        }
    )
    def delete(self, request, pk, format=None):
        """
        Handle DELETE request to remove a specific watchlist entry.
        """
        watchlist_item = get_object_or_404(Watchlist, pk=pk, user=request.user)
        watchlist_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



"""
class MovieListView(generics.ListAPIView):
 
    Retrieves a list of movies.
   

    permission_classes = [permissions.AllowAny]
    queryset = Movie.objects.all()
    serializer_class =  MovieMinimalSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['title', 'release_date', 'genres__name', 'language']
    ordering_fields = ['title', 'release_date']
    ordering = ['title']
    search_fields = ['title', 'genre', 'cast']

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class MovieCreateView(generics.CreateAPIView):

    Create a new movie.

    permission_classes = [permissions.IsAdminUser]
    serializer_class = MovieMinimalSerializer
    queryset = Movie.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class MovieDetailView(APIView):

    Retrieve, update or delete a movie instance.
 
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, identifier, format=None):
        movie = get_object_by_id_or_slug(Movie, identifier, slug_field='slug')
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    def put(self, request,identifier, format=None):
        movie = get_object_by_id_or_slug(Movie, identifier, slug_field='slug')
        serializer = MovieMinimalSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, identifier, format=None):
        movie = get_object_by_id_or_slug(Movie, identifier, slug_field='slug')
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
"""