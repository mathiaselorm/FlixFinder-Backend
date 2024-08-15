from rest_framework import serializers
from .models import Rating

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'movie', 'user', 'score', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate_score(self, value):
        """
        Check that the score is within the 1 to 5 range.
        """
        if not (1 <= value <= 5):
            raise serializers.ValidationError("The score must be between 1 and 5.")
        return value