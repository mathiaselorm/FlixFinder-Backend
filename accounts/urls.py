from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)



urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('auth/google/', views.GoogleAuthView.as_view(), name='google_auth'),
    path('auth/apple/', views.AppleAuthView.as_view(), name='apple_auth'),
    path('user/profile_details/', views.UserDetailView.as_view(), name='user_detail'),
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset-request'),
    path('password/reset/confirm/', views.PasswordResetView.as_view(), name='password_reset-confirm'),
    path('login/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/total/', views.total_users_view, name='total-users'),
    
    
]
