from rest_framework import serializers
from .models import Artisan, HireRequest, ArtisanReview


class ArtisanSerializer(serializers.ModelSerializer):
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Artisan
        fields = [
            "id",
            "full_name",
            "skill",
            "phone",
            "rating",
            "address",
            "city",
            "state",
            "latitude",
            "longitude",
            "created_at",
            "review_count",
        ]

    def get_review_count(self, obj):
        return obj.reviews.count()


class HireRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HireRequest
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = ArtisanReview
        fields = [
            "id",
            "user_name",
            "rating",
            "comment",
            "created_at",
        ]

