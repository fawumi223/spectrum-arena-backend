from django.contrib import admin
from .models import Savings, SavingsTransaction


# ----------------------------------------------------------
# INLINE: Show all transactions inside the Savings detail page
# ----------------------------------------------------------
class SavingsTransactionInline(admin.TabularInline):
    model = SavingsTransaction
    extra = 0
    readonly_fields = ("type", "amount", "note", "created_at")


# ----------------------------------------------------------
# SAVINGS ADMIN
# ----------------------------------------------------------
@admin.register(Savings)
class SavingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "amount",
        "locked_until",
        "is_released",
        "created_at",
        "released_at",
    )

    list_filter = ("is_released", "locked_until", "created_at")
    search_fields = ("user__email", "user__full_name")

    inlines = [SavingsTransactionInline]


# ----------------------------------------------------------
# STANDALONE TRANSACTION ADMIN
# ----------------------------------------------------------
@admin.register(SavingsTransaction)
class SavingsTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "savings", "type", "amount", "note", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("savings__user__email", "note")

