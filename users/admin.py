from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan_type",
        "amount",
        "status",
        "reference",
        "created_at",
    )
    list_filter = ("plan_type", "status", "created_at")
    search_fields = (
        "user__phone_number",
        "user__full_name",
        "reference",
    )
    readonly_fields = ("created_at", "updated_at", "reference")
    ordering = ("-created_at",)

    fieldsets = (
        ("Transaction Info", {
            "fields": ("user", "plan_type", "amount", "reference", "status")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def has_add_permission(self, request):
        """
        Disallow manual transaction creation from admin.
        Transactions should only come from payment processing (Providus API).
        """
        return False

