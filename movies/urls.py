from django.urls import path
from . import views



urlpatterns = [
    # urls for Movie
    path('genres/<str:genre_slug>/movies/', views.GenreMoviesListView.as_view(), name='genre-movies-list'),
    path('genres/<str:genre_slug>/movies/<str:identifier>/', views.MovieDetailView.as_view(), name='movie-detail'),
    path('genres/<str:genre_slug>/movies/<str:identifier>/update/', views.MovieUpdateView.as_view(), name='movie-update'),
    path('genres/<str:genre_slug>/movies/<str:identifier>/delete/', views.MovieDeleteView.as_view(), name='movie-delete'),
    path('movies/top-rated/', views.TopRatedMoviesView.as_view(), name='top-rated-movies'),

    
    #path('movies/', views.MovieListView.as_view(), name='movie-list'),
    #path('movies/new/', views.MovieCreateView.as_view(), name='movie-create'),
    #path('movies/<str:identifier>/', views.MovieDetailView.as_view(), name='movie-detail'),
    path('movies/top-rated/', views.TopRatedMoviesView.as_view(), name='top-rated-movies'),
    
    # urls for Genre
    path('genres/', views.GenreListView.as_view(), name='genre-list'), 
    path('genres/new/', views.GenreCreateView.as_view(), name='genre-create'),  
    path('genres/<str:identifier>/', views.GenreDetailView.as_view(), name='genre-detail'),
    path('genres/<str:identifier>/update/', views.GenreUpdateDeleteView.as_view(), name='genre-update'),
    path('genres/<str:identifier>/delete/', views.GenreUpdateDeleteView.as_view(), name='genre-delete'),		
    
    #urls for comments
    path('genres/<str:genre_slug>/movies/<str:identifier>/comments/', views.MovieCommentsView.as_view(), name='movie-comments'),

    
    path('users/watchlist/create/', views.WatchlistCreateView.as_view(), name='watchlist-create'),
    path('users/watchlist/', views.WatchlistListView.as_view(), name='watchlist-list'),
    path('users/watchlist/update/<int:pk>/', views.WatchlistUpdateView.as_view(), name='watchlist-update'),	
    path('users/watchlist/delete/<int:pk>/', views.WatchlistDeleteView.as_view(), name='watchlist-delete'),

]
