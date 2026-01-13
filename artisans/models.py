from django.conf import settings
from django.db import models


class Artisan(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    skill = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    rating = models.FloatField(default=0)

    # Replacing PointField with latitude & longitude floats
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Extra fields
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.skill}"


class HireRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hire_requests"
    )
    artisan = models.ForeignKey(
        Artisan, on_delete=models.CASCADE, related_name="hire_requests"
    )

    description = models.TextField()
    address = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"HireRequest by {self.user} for {self.artisan}"


class ArtisanReview(models.Model):
    artisan = models.ForeignKey(
        Artisan, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    rating = models.IntegerField(default=5)  # 1–5 stars
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Recalculate rating
        from django.db.models import Avg
        avg_rating = ArtisanReview.objects.filter(artisan=self.artisan).aggregate(
            Avg("rating")
        )["rating__avg"] or 0

        self.artisan.rating = round(avg_rating, 1)
        self.artisan.save()

    def __str__(self):
        return f"Review {self.rating}★ by {self.user} for {self.artisan}"

