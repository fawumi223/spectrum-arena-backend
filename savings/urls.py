from django.urls import path
from .views import (
    CreateSavingsView,
    UserSavingsView,
    GenerateWithdrawalOTPView,
    WithdrawSavingsView,
    SavingsActivityView,
)

urlpatterns = [
    path("create/", CreateSavingsView.as_view()),
    path("me/", UserSavingsView.as_view()),
    path("otp/", GenerateWithdrawalOTPView.as_view()),
    path("withdraw/<int:savings_id>/", WithdrawSavingsView.as_view()),
    path("activity/", SavingsActivityView.as_view()),
]

