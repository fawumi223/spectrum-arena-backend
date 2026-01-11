from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Artisan, HireRequest, ArtisanReview
from .serializers import (
    ArtisanSerializer,
    HireRequestSerializer,
    ReviewSerializer,
)


# -----------------------------------------
# SINGLE ARTISAN DETAIL
# -----------------------------------------
class ArtisanDetailView(APIView):
    def get(self, request, id):
        artisan = Artisan.objects.filter(id=id).first()
        if not artisan:
            return Response({"error": "Artisan not found"}, status=404)

        serializer = ArtisanSerializer(artisan)
        return Response(serializer.data)


# -----------------------------------------
# ALL ARTISANS (GeoJSON)
# -----------------------------------------
class ArtisanListView(generics.ListAPIView):
    queryset = Artisan.objects.all()
    serializer_class = ArtisanSerializer

# -----------------------------------------
# NEARBY SEARCH
# -----------------------------------------
class NearbyArtisansView(APIView):
    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius = float(request.query_params.get("radius", 10))

        if not lat or not lng:
            return Response({"error": "lat and lng are required"}, status=400)

        try:
            user_location = Point(float(lng), float(lat), srid=4326)
        except:
            return Response({"error": "Invalid coordinates"}, status=400)

        artisans = Artisan.objects.annotate(
            distance=Distance("location", user_location)
        ).filter(
            distance__lte=radius * 1000
        )

        # SKILL FILTER
        skill = request.query_params.get("skill")
        if skill:
            artisans = artisans.filter(skill__icontains=skill)

        # SEARCH TEXT
        q = request.query_params.get("q")
        if q:
            artisans = artisans.filter(
                models.Q(full_name__icontains=q) |
                models.Q(skill__icontains=q)
            )

        artisans = artisans.order_by("distance")

        serializer = ArtisanSerializer(artisans, many=True)
        return Response(serializer.data)


# -----------------------------------------
# HIRE AN ARTISAN
# -----------------------------------------
class HireArtisanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        artisan = Artisan.objects.filter(id=id).first()
        if not artisan:
            return Response({"error": "Artisan not found"}, status=404)

        data = {
            "user": request.user.id,
            "artisan": artisan.id,
            "description": request.data.get("description"),
            "address": request.data.get("address"),
            "date": request.data.get("date"),
        }

        serializer = HireRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Hire request submitted successfully!"})

        return Response(serializer.errors, status=400)


# -----------------------------------------
# GET ALL REVIEWS
# -----------------------------------------
class ArtisanReviewsView(APIView):
    def get(self, request, id):
        artisan = Artisan.objects.filter(id=id).first()
        if not artisan:
            return Response({"error": "Artisan not found"}, status=404)

        reviews = ArtisanReview.objects.filter(artisan=artisan).order_by("-created_at")
        serializer = ReviewSerializer(reviews, many=True)

        return Response(serializer.data)


# -----------------------------------------
# POST A NEW REVIEW
# -----------------------------------------
class AddReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        artisan = Artisan.objects.filter(id=id).first()
        if not artisan:
            return Response({"error": "Artisan not found"}, status=404)

        review = ArtisanReview.objects.create(
            artisan=artisan,
            user=request.user,
            rating=request.data.get("rating"),
            comment=request.data.get("comment", "")
        )

        return Response({"message": "Review added successfully!"})

