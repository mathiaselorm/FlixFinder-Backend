from django.urls import path
from .views import predict_rating_view, recommend_movies_view

urlpatterns = [
    path('predict-rating/', predict_rating_view, name='predict_rating'),
    
    path('recommend-movies/',  recommend_movies_view, name='recommend_movie'),
]
