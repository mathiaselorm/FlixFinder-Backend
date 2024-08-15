from django.urls import path
from . import views

urlpatterns = [
    path('movies/<int:movie_id>/ratings/', views.RatingListView.as_view(), name='rating-list'),
    path('ratings/<int:pk>/', views.RatingDetailView.as_view(), name='rating-detail'),
]
