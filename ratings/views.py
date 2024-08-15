from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from .models import Rating, Movie
from .serializers import RatingSerializer

class RatingListView(APIView):
    """
    List all ratings for a specific movie or create a new rating.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, movie_id, format=None):
        movie = get_object_or_404(Movie, pk=movie_id)
        ratings = Rating.objects.filter(movie=movie)
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)

    def post(self, request, movie_id, format=None):
        movie = get_object_or_404(Movie, pk=movie_id)
        serializer = RatingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user, movie=movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RatingDetailView(APIView):
    """
    Retrieve, update, or delete a rating.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk, format=None):
        rating = get_object_or_404(Rating, pk=pk)
        serializer = RatingSerializer(rating)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        rating = get_object_or_404(Rating, pk=pk)
        if request.user != rating.user:
            return Response({'detail': 'You do not have permission to edit this rating.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = RatingSerializer(rating, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        rating = get_object_or_404(Rating, pk=pk)
        if request.user != rating.user:
            return Response({'detail': 'You do not have permission to delete this rating.'}, status=status.HTTP_403_FORBIDDEN)
        rating.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
