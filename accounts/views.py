from django.shortcuts import render
import logging
from django.contrib.auth import get_user_model
from rest_framework import status, views, permissions, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import firebase_admin
from firebase_admin import auth as firebase_auth
from accounts.authentication.firebase_authentication import FirebaseAuthentication
from .utils import UserManager
from .serializers import *

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    firebase_admin.initialize_app()

User = get_user_model()

class RegisterView(views.APIView):
    """
    API endpoint for registering a new user.
    Allows any user to register to the system using an email and password.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        request_body=RegisterSerializer,
        responses={201: UserSerializer, 400: "Bad Request"}
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(token),
                'access': str(token.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoogleAuthView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Authenticate via Google OAuth2",
        request_body=GoogleAuthSerializer,
        responses={200: UserSerializer, 400: "Bad Request"}
    )
    def post(self, request, *args, **kwargs):
        serializer = GoogleAuthSerializer(data=request.data)
        if serializer.is_valid():
            id_token = serializer.validated_data.get('id_token')
            firebase_auth = FirebaseAuthentication()
            decoded_token, error = firebase_auth.authenticate_token(id_token)

            if not decoded_token:
                logger.error(f'Authentication failed: {error}')
                return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

            user, error = UserManager.handle_user(decoded_token)
            if user:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token
                logger.info(f'User authenticated: {user.email}')
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(access)
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f'User management error: {error}')
                return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
        logger.error(f'Invalid data: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AppleAuthView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Authenticate via Apple OAuth2",
        request_body=AppleAuthSerializer,
        responses={200: UserSerializer, 400: "Bad Request"}
    )
    def post(self, request, *args, **kwargs):
        serializer = AppleAuthSerializer(data=request.data)
        if serializer.is_valid():
            id_token = serializer.validated_data.get('identity_token')
            firebase_auth = FirebaseAuthentication()
            decoded_token, error = firebase_auth.authenticate_token(id_token)

            if not decoded_token:
                logger.error(f'Authentication failed: {error}')
                return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)

            user, error = UserManager.handle_user(decoded_token)
            if user:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token
                logger.info(f'User authenticated: {user.email}')
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(access)
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f'User management error: {error}')
                return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
        logger.error(f'Invalid data: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API endpoint for obtaining JWT tokens with custom claims.
    Generates access and refresh JWT tokens for authenticated users.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="Obtain JWT tokens",
        responses={200: "Tokens obtained", 400: "Bad Request"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    

class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a user instance.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Retrieve User Details")
    def get(self, request, *args, **kwargs):
        """
        Retrieve the details of a user.
        """
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update User Details")
    def put(self, request, *args, **kwargs):
        """
        Update the details of a user.
        """
        return self.update(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_summary="Partially Update User Details")
    def patch(self, request, *args, **kwargs):
        """
        Partially update the details of a user.
        """
        kwargs['partial'] = True
        return self.put(request, *args, **kwargs)
    

class PasswordResetRequestView(views.APIView):
    """
    API endpoint to request a password reset via email.
    Initiates the process of sending a password reset link to the user's email.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Request Password Reset",
        request_body=PasswordResetRequestSerializer,
        responses={200: "Password reset email sent", 400: "Bad Request"}
    )
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Implement your logic to send a reset email here
            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(views.APIView):
    """
    API endpoint to reset a user's password.
    Handles the actual password change using a valid reset token.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Reset Password",
        request_body=PasswordResetSerializer,
        responses={200: "Password has been reset successfully", 400: "Bad Request"}
    )
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            # Implement password reset logic here, including token verification
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(ListAPIView):
    """
    List all users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  
   
   
@api_view(['GET'])
def total_users_view(request):
    """
    Get the total number of users.
    """
    total_users = User.objects.count()
    return Response({"total_users": total_users})
