from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import PhoneTokenObtainPairView

urlpatterns = [
    path("", PhoneTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

