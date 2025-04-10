import os
import pandas as pd
from django.conf import settings
import pickle
from django.db.models import Count, Q
from movies.models import Movie
from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from ratings.models import Rating
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from django.contrib.auth import get_user_model
import json
User = get_user_model()



def get_ratings_dataset():
    """
    Fetches ratings data from the database and returns a Surprise dataset object ready for training.
    """
    # Query the database for ratings
    ratings_query = Rating.objects.all().values_list('user_id', 'movie_id', 'score')

    # Create a DataFrame
    ratings_df = pd.DataFrame(list(ratings_query), columns=['user', 'item', 'rating'])

    # Define the reader with the rating scale
    reader = Reader(rating_scale=(0.0, 10.0))  # Adjust the scale if your ratings range differently

    # Load the dataset from the DataFrame
    data = Dataset.load_from_df(ratings_df, reader)
    
    return data


def train_model():
    # Load the ratings dataset
    data = get_ratings_dataset()
    
    
    # Load the data into Surprise's format
    reader = Reader(rating_scale=(1, 10))
    dataset = Dataset.load_from_df(data.df[['user', 'item', 'rating']], reader)
    trainset = dataset.build_full_trainset()
    
    
    # Train the SVD algorithm with optimized parameters
    algo = SVD(n_epochs=20, lr_all=0.01, reg_all=0.2)
    algo.fit(trainset)
    
    
     # Save the trained model to a file
    file_path = r'C:\Users\Melarc.py\Documents\GitHub\Backend\FlixFinder\recommendation\models\trained_model.pkl'
    with open(file_path, 'wb') as file:
        pickle.dump(algo, file)
        
    # Also save the trained model to Django's storage
    django_path = 'recommendation/models/trained_model.pkl'
    model_data = pickle.dumps(algo)
    if default_storage.exists(django_path):
        default_storage.delete(django_path)
    default_storage.save(django_path, ContentFile(model_data))
    
    print("Model trained and saved successfully both locally and in Django storage!")


def load_model():
    """
    Loads the trained SVD model from a file.
    """
    # Define the path to the model file
    file_path = r'C:\Users\Melarc.py\Documents\GitHub\Backend\FlixFinder\recommendation\models\trained_model.pkl'
    #file_path = 'recommendation/models/trained_model.pkl' For production
    
    # Load the model from the file
    with open(file_path, 'rb') as file:
        model = pickle.load(file)
    
    print("Model loaded successfully!")
    return model


def predict_rating(user_id, movie_id):
    # Load the trained SVD model
    algo = load_model()

    # Predict the rating that the user might give to the movie
    prediction = algo.predict(uid=str(user_id), iid=str(movie_id))
    return prediction.est




def get_top_n_recommendations(user_id, n=10):
    # Load the trained model
    algo = load_model()
    
    # Get all movies
    all_movies = Movie.objects.all().values_list('id', flat=True)
    
    # Get movies already rated by the user
    rated_movies = Rating.objects.filter(user_id=user_id).values_list('movie_id', flat=True)
    
    # Predict ratings for all movies that the user hasn't rated yet
    predictions = []
    for movie_id in set(all_movies) - set(rated_movies):
        predicted = algo.predict(user_id, movie_id)
        predictions.append((movie_id, predicted.est))
    
    # Sort the predictions based on the estimated rating
    predictions.sort(key=lambda x: x[1], reverse=True)
    
    # Return the top n predictions
    top_n = predictions[:n]
    return [(Movie.objects.get(id=movie_id), rating) for movie_id, rating in top_n]



def recommend_based_on_genres(user_id, n=10):
    """
    Recommends movies based on the user's preferred genres.
    - If the user has one or more preferred genres, recommend movies matching any of those genres.
    - If the user has no preferred genres, recommend top-rated movies.
    """
    user = User.objects.get(id=user_id)
    
    # Ensure that preferences are treated as a dictionary if stored as a string
    if isinstance(user.preferences, str):
        user.preferences = json.loads(user.preferences)

    preferred_genres = user.preferences.get('genres', [])
    
    if not preferred_genres:
        # If the user has no genre preferences, return top rated movies
        top_movies = Movie.objects.order_by('-average_rating')[:n]
        return [(movie, movie.average_rating) for movie in top_movies]

     # Adjust the query to handle one or more genres appropriately
    if len(preferred_genres) == 1:
        # If only one genre is preferred, filter directly without annotation
        genre_matched_movies = Movie.objects.filter(genres__name=preferred_genres[0])
    else:
        # For multiple genres, use the previous approach
        genre_matched_movies = Movie.objects.filter(
            genres__name__in=preferred_genres
        ).annotate(
            matched_genres=Count('genres', filter=Q(genres__name__in=preferred_genres))
        ).filter(matched_genres__gte=2).distinct()

    top_movies = genre_matched_movies.order_by('-average_rating')[:n]
    return [(movie, movie.average_rating) for movie in top_movies]