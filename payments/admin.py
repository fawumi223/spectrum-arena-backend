from django.contrib import admin
from .models import SavedCard


@admin.register(SavedCard)
class SavedCardAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "card_type",
        "last4",
        "bank",
        "reusable",
        "is_active",
        "created_at",
    )
    search_fields = (
        "last4",
        "authorization_code",
        "user__phone_number",
    )
    list_filter = (
        "reusable",
        "is_active",
        "bank",
    )

