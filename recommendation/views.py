from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from .utils import recommend_movies_by_user_genre, recommend_movies_by_user_preferences
import pandas as pd
from accounts.models import CustomUser
import logging
import json





logger = logging.getLogger(__name__)

class RecommendMoviesAPIView(APIView):

    def get(self, request, user_id):
        try:
            recommended_movies = recommend_movies_by_user_genre(user_id)
            if not recommended_movies:
                return Response({"detail": "No movies found for the given preferences."}, status=status.HTTP_404_NOT_FOUND)
            
            movies_data = [
                {   'id': movie.id,
                    'title': movie.title,
                    'overview': movie.overview,
                    'release_date': movie.release_date,
                    'language': movie.language,
                    'poster': movie.poster_url,
                    'trailers': movie.trailer_url,
                    'genres': ', '.join(genre.name for genre in movie.genres.all()),
                    'rating': movie.average_rating,
                }
                for movie in recommended_movies
            ]
            return Response(movies_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error while generating recommendations for user {user_id}: {str(e)}")
            return Response({"detail": "An error occurred while generating recommendations."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




def get_recommendations(request, user_id):
    try:
        # Load the similarity matrix
        similarity_df = pd.read_csv("C:\\Users\\Melarc.py\\Documents\\GitHub\\Flix\\data\\similarity_matrix.csv", index_col=0)
        
        # Fetch user preferences
        user = CustomUser.objects.get(pk=user_id)
        try:
            # Try to parse preferences if it's stored as a JSON string
            preferences = json.loads(user.preferences)
        except TypeError:
            # If it's already a dictionary, use it directly
            preferences = user.preferences

        user_genres = preferences.get('genres', [])
        
        # Get recommendations
        recommendations = recommend_movies_by_user_preferences(similarity_df, user_genres)
        
        # Prepare the response data
        data = {
            "user_id": user_id,
            "recommendations": recommendations
        }
        return JsonResponse(data, safe=False)
    
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)