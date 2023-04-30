from rest_framework import serializers
from applications.review.models import Review
from django.contrib.auth import get_user_model

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.CharField(required=False)
    
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewed_user_id', 'review', 'created_at', 'updated_at']
                

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['reviewed_user'] = instance.reviewed_user_id.username
        representation['reviewer_username'] = instance.reviewer.username
        return representation