import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from movies.serializers import WatchlistSerializer

logger = logging.getLogger(__name__)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    watchlist = WatchlistSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number', 
            'date_of_birth', 'gender', 'preferences', 'location', 
            'date_joined', 'last_login', 'is_active', 'is_staff', 
            'profile_picture', 'bio', 'watchlist'  # Include 'watchlist' here
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_active', 'is_staff', 'watchlist']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    """
    password = serializers.CharField(write_only=True, required=True, min_length=8, label=_("Password"), style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, min_length=8, label=_("Confirm Password"), style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'password_confirm', 'date_of_birth', 'gender', 'location']

    def validate(self, data):
        """
        Check that the two password entries match and meet security requirements.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        if not any(char.isdigit() for char in data['password']):
            raise serializers.ValidationError({"password": _("Password must include at least one numeral.")})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        try:
            user = User.objects.create_user(**validated_data)
            logger.info(f"User created successfully: {user.email}")
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {e}")
            raise serializers.ValidationError({"user": _("An unexpected error occurred. Please try again.")})
        return user

class GoogleAuthSerializer(serializers.Serializer):
    """
    Serializer for Google OAuth2 authentication.
    """
    id_token = serializers.CharField(write_only=True, required=True)

class AppleAuthSerializer(serializers.Serializer):
    """
    Serializer for Apple OAuth2 authentication.
    """
    identity_token = serializers.CharField(write_only=True, required=True)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer to include user data.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # Add extra responses here
        data['user'] = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'phone_number': self.user.phone_number,
            'date_of_birth': self.user.date_of_birth,
            'is_active': self.user.is_active,
        }
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email Address"))

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            logger.error(f"Password reset requested for non-existent email: {value}")
            raise serializers.ValidationError(_("No user is associated with this email address."))
        return value

class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8, label=_("New Password"), style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, min_length=8, label=_("Confirm New Password"), style={'input_type': 'password'})

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            logger.error("Password reset attempt with non-matching passwords.")
            raise serializers.ValidationError({"confirm_password": _("The two password fields must match.")})
        
        return data