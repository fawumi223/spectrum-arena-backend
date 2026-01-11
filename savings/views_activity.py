from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import SavingsTransaction
from .serializers import SavingsTransactionSerializer


class SavingsActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        transactions = SavingsTransaction.objects.filter(
            savings__user=user
        ).order_by("-created_at")

        serializer = SavingsTransactionSerializer(transactions, many=True)

        return Response(serializer.data)

