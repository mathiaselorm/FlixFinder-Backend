
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from .models import Movie, Genre, Comment, Watchlist
from .serializers import MovieSerializer, GenreSerializer, CommentSerializer, MovieMinimalSerializer, GenreMinimalSerializer, WatchlistSerializer
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
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
        operation_description="Retrieve a comprehensive list of all genres available in the database.",
        responses={
            200: openapi.Response(
                description="A list of all genres successfully retrieved.",
                schema=GenreMinimalSerializer(many=True),
                examples={
                    'application/json': {
                        "genres": [
                            {"id": 1, "name": "Rock"},
                            {"id": 2, "name": "Jazz"},
                            {"id": 3, "name": "Classical"}
                        ]
                    }
                }
            ),
            500: openapi.Response(
                description="Internal Server Error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Detailed error information")
                    },
                    example={
                        "message": "Internal server error",
                        "error": "Database connection failed"
                    }
                )
            )
        },
        tags=['Genres'],
        operation_id="list_genres",
        operation_summary="Get a List of Genres",
        security=[]
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
        operation_description="Create a new genre in the database.",
        request_body=GenreMinimalSerializer,
        responses={
            201: openapi.Response(
                description="Genre successfully created.",
                schema=GenreMinimalSerializer,
                examples={
                    'application/json': {
                        "id": 4,
                        "name": "Blues"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - Invalid data provided.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description="Error details for the name field.")
                    },
                    example={
                        "name": ["This field is required."]
                    }
                )
            )
        },
        tags=['Genres'],
        operation_id="create_genre",
        operation_summary="Create a New Genre",
        security=[{'bearerAuth': []}]  
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
        operation_description="Retrieve detailed information about a specific genre using its ID or slug.",
        manual_parameters=[
            openapi.Parameter(
                name='identifier',
                in_=openapi.IN_PATH,
                description="The unique identifier (ID or slug) of the genre to retrieve.",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Detailed information about the genre.",
                schema=GenreSerializer,
                examples={
                    'application/json': {
                        "id": 1,
                        "name": "Rock",
                        "description": "A genre of popular music that originated as 'rock and roll' in the United States in the early 1950s."
                    }
                }
            ),
            404: openapi.Response(
                description="Genre not found.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={
                        "error": "Genre not found"
                    }
                )
            )
        },
        tags=['Genres'],
        operation_id="get_genre_detail",
        operation_summary="Get Detailed Genre Information",
        security=[]
    )
    def get(self, request, identifier, format=None):
        genre = get_object_by_id_or_slug(Genre, identifier, slug_field='slug')
        if genre:
            serializer = GenreSerializer(genre, context={'request': request, 'view': self})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Genre not found"}, status=status.HTTP_404_NOT_FOUND)
        

class GenreUpdateDeleteView(APIView):
    """
    Updates or deletes a genre based on the provided identifier.

    Accessible only to authenticated users, this endpoint allows for updating or deleting genres identified by their
    unique ID or slug. Suitable for administrative tasks or user-generated content management.

    PUT: Updates the specified genre with the provided data.
    DELETE: Deletes the specified genre.
    """
    permission_classes = [permissions.IsAuthenticated] 

    @swagger_auto_schema(
        operation_description="Update an existing genre using its ID or slug.",
        request_body=GenreSerializer,
        responses={
            200: openapi.Response(
                description="Genre successfully updated.",
                schema=GenreSerializer,
                examples={
                    'application/json': {
                        "id": 1,
                        "name": "Rock",
                        "description": "A broad genre of popular music based on rock and roll."
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - Invalid data provided.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description="Error details for the name field.")
                    },
                    example={
                        "name": ["This field must not be blank."]
                    }
                )
            ),
            404: 'Genre not found'
        },
        manual_parameters=[
            openapi.Parameter(
                name='identifier',
                in_=openapi.IN_PATH,
                description="The unique identifier (ID or slug) of the genre to update.",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        tags=['Genres'],
        operation_id="update_genre",
        operation_summary="Update Genre Details",
        security=[{'bearerAuth': []}]  # Assuming JWT Bearer token is used for auth
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
        operation_description="Delete a specific genre using its ID or slug.",
        responses={
            204: 'No Content',
            404: openapi.Response(
                description="Genre not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={
                        "error": "Genre not found"
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter(
                name='identifier',
                in_=openapi.IN_PATH,
                description="The unique identifier (ID or slug) of the genre to delete.",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        tags=['Genres'],
        operation_id="delete_genre",
        operation_summary="Delete Genre",
        security=[{'bearerAuth': []}]  # Assuming JWT Bearer token is used for auth
    )
    def delete(self, request, identifier, format=None):
        genre = get_object_by_id_or_slug(Genre, identifier, slug_field='slug')
        if not genre:
            return Response({"error": "Genre not found"}, status=status.HTTP_404_NOT_FOUND)

        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class GenreMoviesListView(generics.ListAPIView):
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
                description="The slug of the genre to filter movies by, facilitating targeted retrieval of movies associated with a specific genre.",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="A list of movies associated with the specified genre.",
                schema=MovieMinimalSerializer(many=True),
                examples={
                    'application/json': {
                        "movies": [
                            {"id": 1, "title": "Inception", "release_date": "2010-07-16"},
                            {"id": 2, "title": "Interstellar", "release_date": "2014-11-07"}
                        ]
                    }
                }
            ),
            404: openapi.Response(
                description="Genre not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={
                        "error": "Genre not found"
                    }
                )
            )
        },
        tags=['Movies by Genre']
    )
    def get_queryset(self):
        """
        Fetches movies that belong to a specific genre identified by 'genre_slug'.
        Caches the genre object and its movies if not already cached.
        """
        cache_key = f"genre_movies_{self.kwargs['genre_slug']}"
        cached_genre_movies = cache.get(cache_key)

        if cached_genre_movies:
            return cached_genre_movies

        genre = get_object_or_404(Genre, slug=self.kwargs['genre_slug'])
        movies = genre.movies.all().prefetch_related('genres')
        cache.set(cache_key, movies, timeout=3600)  # Cache for 1 hour
        return movies

    

class MovieDetailView(APIView):
    """
    Retrieves detailed information about a movie identified by its slug or identifier within a specific genre.
    
    This endpoint is publicly accessible and ensures detailed movie information is only provided if the movie is
    associated with the specified genre. If not, a 404 error is returned.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific movie within a genre.",
        manual_parameters=[
            openapi.Parameter(
                'genre_slug',
                openapi.IN_PATH,
                description="Slug of the genre to which the movie belongs.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'identifier',
                openapi.IN_PATH,
                description="Identifier or slug of the movie. This can be the movie's ID or its URL-friendly slug.",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Detailed information about the movie.",
                schema=MovieSerializer,
                examples={
                    'application/json': {
                        "id": 10,
                        "title": "The Great Escape",
                        "release_date": "1963-07-04",
                        "genres": [
                            {"id": 1, "name": "War"},
                            {"id": 2, "name": "Adventure"}
                        ],
                        "director": "John Sturges",
                        "cast": "Steve McQueen, James Garner, Richard Attenborough",
                        "description": "Allied prisoners of war plan for several hundred of their number to escape from a German camp during World War II."
                    }
                }
            ),
            404: openapi.Response(
                description="Movie not found in the specified genre",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={
                        "error": "Movie not found in the specified genre"
                    }
                )
            )
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
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        if not movie.genres.filter(slug=genre_slug).exists():
            return Response({"error": "Movie not found in the specified genre"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MovieSerializer(movie, context={'request': request})
        return Response(serializer.data)


class MovieUpdateView(APIView):
    """
    Updates the details of a movie identified by its slug or identifier within a specific genre.
    
    This endpoint allows authenticated users to update movie details, ensuring that the movie belongs to the specified genre.
    If the movie does not exist under the specified genre or if data validation fails, appropriate error responses are returned.
    """
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_description="Update details of a specific movie within a genre based on provided data.",
        request_body=MovieSerializer,
        responses={
            200: openapi.Response(
                description="Successfully updated movie details.",
                schema=MovieSerializer,
                examples={
                    'application/json': {
                        "id": 25,
                        "title": "The Revenant",
                        "release_date": "2015-12-16",
                        "genres": [{"id": 3, "name": "Adventure"}, {"id": 4, "name": "Drama"}],
                        "director": "Alejandro González Iñárritu",
                        "cast": "Leonardo DiCaprio, Tom Hardy",
                        "description": "A frontiersman on a fur trading expedition in the 1820s fights for survival after being mauled by a bear and left for dead by members of his own hunting team."
                    }
                }
            ),
            400: openapi.Response(
                description="Validation errors occurred.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'field_name': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description="List of errors for each field")
                    },
                    example={
                        "title": ["This field may not be blank."],
                        "release_date": ["Invalid date format."]
                    }
                )
            ),
            404: openapi.Response(
                description="Movie not found in the specified genre.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={
                        "error": "Movie not found in the specified genre"
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter('genre_slug', openapi.IN_PATH, description="Slug of the genre to which the movie belongs", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('identifier', openapi.IN_PATH, description="Identifier or slug of the movie to be updated", type=openapi.TYPE_STRING, required=True)
        ],
        tags=['Movie Update']
    )
    def put(self, request, genre_slug, identifier):
        """
        Updates a movie specified by its identifier or slug within a given genre based on the provided data.
        Validates the existence of the movie within the specified genre before attempting an update.
        If the movie is not found under the specified genre or if data validation fails, appropriate error messages and status codes are returned.
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
    Deletes a movie from a specific genre based on the movie's slug.

    This endpoint allows authenticated users to delete a movie identified by its slug within a specific genre.
    It verifies the movie's association with the genre before proceeding with deletion.
    """
    permission_classes = [permissions.IsAdminUser]  

    @swagger_auto_schema(
        operation_description="Delete a specific movie from a genre based on the movie's slug.",
        manual_parameters=[
            openapi.Parameter(
                'genre_slug',
                openapi.IN_PATH,
                description="Slug of the genre from which the movie is to be deleted.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'identifier',
                openapi.IN_PATH,
                description="Identifier or slug of the movie to be deleted.",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: openapi.Response(
                description="No Content. Movie deleted successfully."
            ),
            404: openapi.Response(
                description="Not Found. Movie not found in the specified genre.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={
                        "error": "Movie not found in the specified genre"
                    }
                )
            )
        },
        tags=['Movie Deletion']
    )
    def delete(self, request, genre_slug, identifier):
        """
        Deletes a movie specified by its identifier or slug within a given genre.
        Verifies the movie's presence in the specified genre before deletion.
        """
        try:
            # Retrieve the genre
            genre = get_object_by_id_or_slug(Genre, slug=genre_slug)
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
    This endpoint supports both GET and POST methods for authenticated users or read-only access.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Retrieve a list of all comments for a specific movie within a specified genre.",
        manual_parameters=[
            openapi.Parameter(
                name='genre_slug',
                in_=openapi.IN_PATH,
                description="Slug of the genre to which the movie belongs",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name='identifier',
                in_=openapi.IN_PATH,
                description="Slug of the movie for which comments are listed",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="A list of all comments for the movie.",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY, 
                    items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="The ID of the comment"),
                        'user': openapi.Schema(type=openapi.TYPE_STRING, description="Username of the commenter"),
                        'comment': openapi.Schema(type=openapi.TYPE_STRING, description="Comment text"),
                        'date_posted': openapi.Schema(type=openapi.TYPE_STRING, description="Date when the comment was posted", format='date')
                    }),
                ),
                examples={
                    'application/json': [
                        {"id": 1, "user": "john_doe", "comment": "Great movie!", "date_posted": "2024-01-02"},
                        {"id": 2, "user": "jane_doe", "comment": "Really enjoyed the plot.", "date_posted": "2024-01-03"}
                    ]
                }
            ),
            404: "Movie or Genre not found"
        }
    )
    def get_queryset(self):
        """
        Return a list of all comments for the movie specified by the genre_slug and identifier.
        """
        genre = get_object_or_404(Genre, slug=self.kwargs['genre_slug'])
        movie = get_object_or_404(Movie, slug=self.kwargs['identifier'], genres=genre)
        return Comment.objects.filter(movie=movie)

    @swagger_auto_schema(
        operation_description="Create a new comment for a specific movie within a specified genre.",
        request_body=CommentSerializer,
        responses={
            201: openapi.Response(
                description="Successfully created a new comment.",
                schema=CommentSerializer,
                examples={
                    'application/json': {
                        "id": 3,
                        "user": "new_user",
                        "comment": "Incredible cinematography!",
                        "date_posted": "2024-01-04"
                    }
                }
            ),
            400: "Bad Request - Invalid data"
        }
    )
    def perform_create(self, serializer):
        """
        Create a new comment, associating it with the correct movie and the current user.
        """
        genre = get_object_or_404(Genre, slug=self.kwargs['genre_slug'])
        movie = get_object_or_404(Movie, slug=self.kwargs['identifier'], genres=genre)
        serializer.save(user=self.request.user, movie=movie)
        
        

class CommentRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    View to retrieve and update a user's comment.
    This endpoint ensures that only the owner of the comment can see and modify their comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns comments only for the currently authenticated user, ensuring user privacy and data integrity.
        """
        user = self.request.user
        return Comment.objects.filter(user=user)

    def get_object(self):
        """
        Ensures that a user can only access their own comments. Raises PermissionDenied if the comment does not belong to the user.
        """
        comment = super().get_object()
        if comment.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this comment.")
        return comment

    @swagger_auto_schema(
        operation_description="Retrieve and update a user's comment by its ID.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                in_=openapi.IN_PATH,
                description="The ID of the comment to retrieve and update.",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved and updated the comment.",
                schema=CommentSerializer,
                examples={
                    'application/json': {
                        "id": 1,
                        "user": "john_doe",
                        "comment": "This is an updated comment.",
                        "date_posted": "2024-01-02"
                    }
                }
            ),
            403: openapi.Response(
                description="Permission denied - You do not have permission to edit this comment.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={
                        "error": "You do not have permission to edit this comment."
                    }
                )
            ),
            404: "Comment not found",
            400: "Bad Request - Invalid data"
        }
    )
    def put(self, request, *args, **kwargs):
        """
        Handles the PUT request to update a comment. Validates the data and returns the updated comment if successful.
        """
        return super().put(request, *args, **kwargs)
    
    
class CommentDeleteView(generics.DestroyAPIView):
    """
    Allows a user to delete their own comment. Ensures that comments can only be deleted by their respective owners.
    """
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns comments only for the currently authenticated user, ensuring data privacy and ownership enforcement.
        """
        user = self.request.user
        return Comment.objects.filter(user=user)

    def get_object(self):
        """
        Overrides the standard `get_object` method to include a security check, ensuring that the comment belongs to the currently authenticated user before allowing deletion.
        Raises PermissionDenied if the user tries to delete a comment that does not belong to them.
        """
        comment = super().get_object()
        if comment.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this comment.")
        return comment

    @swagger_auto_schema(
        operation_description="Delete a user's comment by its ID.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                in_=openapi.IN_PATH,
                description="The ID of the comment to be deleted.",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: openapi.Response(
                description="Comment successfully deleted."
            ),
            403: openapi.Response(
                description="Permission denied - You do not have permission to delete this comment.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={
                        "error": "You do not have permission to delete this comment."
                    }
                )
            ),
            404: openapi.Response(
                description="Comment not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={
                        "error": "Comment not found"
                    }
                )
            )
        }
    )
    def delete(self, request, *args, **kwargs):
        """
        Handles the DELETE request to delete a comment. If the deletion is successful, a 204 No Content response is returned. 
        Ensures that only the comment's owner can delete the comment.
        """
        return super().delete(request, *args, **kwargs)
    
    

class TopRatedMoviesView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Retrieve Top-Rated Movies",
        operation_description="Fetches a list of movies that have an average rating above a specified threshold. "
                              "This endpoint is useful for finding highly rated movies within the database.",
        manual_parameters=[
            openapi.Parameter(
                name='threshold',
                in_=openapi.IN_QUERY,
                description="The minimum average rating to filter movies by. Defaults to 8.0 if not specified.",
                type=openapi.TYPE_NUMBER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="A list of top-rated movies above the specified threshold.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of movies returned."),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, description="URL to the next page of results.", format=openapi.FORMAT_URI),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, description="URL to the previous page of results.", format=openapi.FORMAT_URI),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Movie ID"),
                                'title': openapi.Schema(type=openapi.TYPE_STRING, description="Title of the movie"),
                                'average_rating': openapi.Schema(type=openapi.TYPE_NUMBER, description="Average rating of the movie"),
                            }),
                            description="Array of top-rated movies."
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request when the threshold value is invalid.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message explaining the invalid input.")
                    }
                )
            )
        }
    )
    def get(self, request, *args, **kwargs):
        # Get the threshold parameter from the request
        threshold = request.query_params.get('threshold', 8.0)
        try:
            # Try to convert the threshold to a float
            threshold = float(threshold)
        except ValueError:
            # If the conversion fails, return an error response
            return Response({"error": "Invalid threshold value."}, status=400)

        # Query the movies that have an average rating greater or equal to the threshold
        queryset = Movie.objects.filter(average_rating__gte=threshold)

        # Initialize the paginator
        paginator = PageNumberPagination()
        paginator.page_size = 10  # You can configure the page size here

        # Paginate the queryset
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            # If pagination is successful, serialize the page of movies
            serializer = MovieMinimalSerializer(page, many=True, context={'request': request})
            # Return the paginated response
            return paginator.get_paginated_response(serializer.data)

        # If no pagination is required (unlikely unless page size is larger than the queryset),
        # serialize and return the entire queryset
        serializer = MovieMinimalSerializer(queryset, many=True, context={'request': request})
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