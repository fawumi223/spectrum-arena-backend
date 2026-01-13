from math import radians, cos, sin, asin, sqrt

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


# Utility: Haversine distance in KM
def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 6371 * 2 * asin(sqrt(a))  # Earth radius in KM


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
# ALL ARTISANS
# -----------------------------------------
class ArtisanListView(generics.ListAPIView):
    queryset = Artisan.objects.all()
    serializer_class = ArtisanSerializer


# -----------------------------------------
# NEARBY SEARCH (Haversine)
# -----------------------------------------
class NearbyArtisansView(APIView):
    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius = float(request.query_params.get("radius", 10))

        if not lat or not lng:
            return Response({"error": "lat and lng are required"}, status=400)

        try:
            user_lat = float(lat)
            user_lng = float(lng)
        except:
            return Response({"error": "Invalid coordinates"}, status=400)

        artisans = Artisan.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

        # Apply optional filters
        skill = request.query_params.get("skill")
        if skill:
            artisans = artisans.filter(skill__icontains=skill)

        q = request.query_params.get("q")
        if q:
            artisans = artisans.filter(
                models.Q(full_name__icontains=q) |
                models.Q(skill__icontains=q)
            )

        # Filter manually by distance
        results = []
        for artisan in artisans:
            dist = haversine(user_lat, user_lng, artisan.latitude, artisan.longitude)
            if dist <= radius:
                results.append((dist, artisan))

        # Sort by distance
        results.sort(key=lambda x: x[0])

        serializer = ArtisanSerializer([a for _, a in results], many=True)
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

        ArtisanReview.objects.create(
            artisan=artisan,
            user=request.user,
            rating=request.data.get("rating"),
            comment=request.data.get("comment", "")
        )

        return Response({"message": "Review added successfully!"})

