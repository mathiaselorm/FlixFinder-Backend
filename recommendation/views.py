from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from movies.models import Movie
from ratings.models import Rating
from .models import RecommendedMovie
from .serializers import RecommendedMovieSerializer
from .utils import predict_rating, get_top_n_recommendations, recommend_based_on_genres

User = get_user_model()

@api_view(['POST'])
@csrf_exempt
def predict_rating_view(request):
    """
    API endpoint that predicts the rating a user would give to a movie.
    """
    user_id = request.data.get('user_id')
    movie_id = request.data.get('movie_id')

    # Validate user and movie IDs
    try:
        user_id = int(user_id)
        movie_id = int(movie_id)
    except (TypeError, ValueError):
        return Response({'error': 'Invalid user_id or movie_id provided.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user and movie exist
    if not User.objects.filter(id=user_id).exists():
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not Movie.objects.filter(id=movie_id).exists():
        return Response({'error': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Predict rating
    predicted_rating = predict_rating(user_id, movie_id)
    
    # Optionally, save or process the prediction
    movie = Movie.objects.get(id=movie_id)
    user = User.objects.get(id=user_id)
    recommended_movie = RecommendedMovie.objects.create(user=user, movie=movie)
    serializer = RecommendedMovieSerializer(recommended_movie)

    return Response({
        'predicted_rating': predicted_rating,
        'recommended_movie': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@csrf_exempt
def recommend_movies_view(request):
    user_id = request.user.id
    if user_id:
        try:
            user_id = int(user_id)
            # Count how many movies the user has rated
            rating_count = Rating.objects.filter(user_id=user_id).count()
            
            if rating_count > 5:  # Threshold for cold start (adjust as needed)
                # Use collaborative filtering
                recommendations = get_top_n_recommendations(user_id, n=10)
            else:
                # Use content-based filtering
                recommendations = recommend_based_on_genres(user_id, n=10)
            
            data = {
                'recommendations': [{
                    'movie_id': movie.id,
                    'title': movie.title,
                    'slug': movie.slug,
                    'overview': movie.overview,
                    'language': movie.language,
                    'release_date': movie.release_date,
                    'poster_url': movie.poster_url,
                    'trailer_url': movie.trailer_url,
                    'average_rating': movie.average_rating,
                    'predicted_rating': rating
                } for movie, rating in recommendations]
            }
            return Response(data, status=200)
        except ValueError:
            return Response({'error': 'Invalid user_id provided.'}, status=400)
    else:
        return Response({'error': 'User ID is required'}, status=400)
