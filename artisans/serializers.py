from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Artisan, HireRequest, ArtisanReview


# -----------------------------------------------------
# ARTISAN SERIALIZER (WITH IMAGE, DISTANCE, RATING)
# -----------------------------------------------------
class ArtisanSerializer(GeoFeatureModelSerializer):
    image = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Artisan
        geo_field = "location"
        fields = (
            "id",
            "full_name",
            "skill",
            "phone",
            "rating",           # stored average rating
            "average_rating",   # live rating (same as rating)
            "review_count",
            "address",
            "city",
            "state",
            "location",
            "image",
            "distance",
        )

    # Return artisan image safely
    def get_image(self, obj):
        try:
            if obj.image:
                return obj.image.url
        except:
            return None
        return None

    # Return distance value
    def get_distance(self, obj):
        if hasattr(obj, "distance") and obj.distance:
            return obj.distance.m  # meters
        return None

    # Return average rating
    def get_average_rating(self, obj):
        return obj.rating  # stored in artisan model

    # Return count of all reviews
    def get_review_count(self, obj):
        return obj.reviews.count()


# -----------------------------------------------------
# HIRE REQUEST SERIALIZER
# -----------------------------------------------------
class HireRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HireRequest
        fields = "__all__"


# -----------------------------------------------------
# ARTISAN REVIEW SERIALIZER
# -----------------------------------------------------
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = ArtisanReview
        fields = (
            "id",
            "user_name",
            "rating",
            "comment",
            "created_at",
        )

