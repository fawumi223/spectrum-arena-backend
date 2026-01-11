from django.urls import path
from .views import (
    ArtisanListView,
    ArtisanDetailView,
    NearbyArtisansView,
    HireArtisanView,
    ArtisanReviewsView,
    AddReviewView,
)

urlpatterns = [
    path("", ArtisanListView.as_view(), name="artisan-list"),
    path("nearby/", NearbyArtisansView.as_view(), name="artisan-nearby"),

    # NEW — artisan profile
    path("<int:id>/", ArtisanDetailView.as_view(), name="artisan-detail"),

    # NEW — hire an artisan
    path("<int:id>/hire/", HireArtisanView.as_view(), name="hire-artisan"),

    # NEW — reviews list + add review
    path("<int:id>/reviews/", ArtisanReviewsView.as_view(), name="artisan-reviews"),
    path("<int:id>/reviews/add/", AddReviewView.as_view(), name="add-review"),
]

