from rest_framework import viewsets, filters, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from math import radians, cos, sin, asin, sqrt
import requests
from .models import JobPost
from .serializers import JobPostSerializer


# -------------------------------------------------------------------------
# Pagination
# -------------------------------------------------------------------------
class JobPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


# -------------------------------------------------------------------------
# Job ViewSet — Secure (JWT required for POST, PUT, DELETE)
# -------------------------------------------------------------------------
class JobViewSet(viewsets.ModelViewSet):
    queryset = JobPost.objects.all().order_by("-created_at")
    serializer_class = JobPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # ✅ JWT protected
    pagination_class = JobPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["company_name", "category", "role", "company_address", "job_type", "job_mode"]
    ordering_fields = ["created_at", "company_name"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        """
        Automatically assign the logged-in user and geocode the company address.
        """
        job = serializer.save(user=self.request.user)
        if job.company_address:
            lat, lon = self.get_coordinates_from_address(job.company_address)
            if lat and lon:
                job.latitude = lat
                job.longitude = lon
                job.save()

    def get_coordinates_from_address(self, address):
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": address, "format": "json", "limit": 1}
            headers = {"User-Agent": "SpectrumArena/1.0"}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            print(f"⚠️ Geocoding failed for '{address}': {e}")
        return None, None


# -------------------------------------------------------------------------
# Public: Nearby Jobs
# -------------------------------------------------------------------------
class NearbyJobsView(APIView):
    permission_classes = [permissions.AllowAny]  # ✅ public

    def get(self, request):
        try:
            user_lat = float(request.query_params.get("lat"))
            user_lng = float(request.query_params.get("lng"))
        except (TypeError, ValueError):
            return Response({"error": "Please provide valid lat and lng parameters."}, status=400)

        radius = float(request.query_params.get("radius", 3))  # miles
        jobs = JobPost.objects.filter(is_active=True)

        nearby = []
        for job in jobs:
            if job.latitude and job.longitude:
                dist = self.haversine(user_lat, user_lng, job.latitude, job.longitude)
                if dist <= radius:
                    nearby.append(job)

        serializer = JobPostSerializer(nearby, many=True)
        return Response({"count": len(nearby), "results": serializer.data}, status=200)

    def haversine(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        miles = 3956 * c
        return miles

