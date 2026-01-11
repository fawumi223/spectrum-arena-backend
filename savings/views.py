from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Savings, SavingsTransaction, SavingsOTP
from .serializers import SavingsSerializer, SavingsTransactionSerializer
from .utils import generate_otp, verify_otp
from .utils import apply_interest, update_goal_status

# --------------------------------------------------------
# CREATE SAVINGS
# --------------------------------------------------------
class CreateSavingsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SavingsSerializer(data=request.data)
        if serializer.is_valid():
            savings = serializer.save(user=request.user)

            # Initial deposit
            SavingsTransaction.objects.create(
                savings=savings,
                type="deposit",
                amount=savings.amount,
                note="Initial deposit"
            )

            return Response(
                {"message": "Savings created successfully!",
                 "data": SavingsSerializer(savings).data},
                status=201
            )
        return Response(serializer.errors, status=400)


# --------------------------------------------------------
# LIST USER SAVINGS
# --------------------------------------------------------
class UserSavingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        savings = Savings.objects.filter(user=request.user)
        return Response(SavingsSerializer(savings, many=True).data, status=200)


# --------------------------------------------------------
# SEND OTP FOR WITHDRAWAL
# --------------------------------------------------------
class GenerateWithdrawalOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        savings_id = request.data.get("savings_id")
        if not savings_id:
            return Response({"error": "savings_id is required"}, status=400)

        try:
            savings = Savings.objects.get(id=savings_id, user=request.user)
        except Savings.DoesNotExist:
            return Response({"error": "Savings not found"}, status=404)

        if not savings.can_withdraw():
            return Response({"error": "Savings is still locked"}, status=400)

        code = generate_otp()
        SavingsOTP.objects.create(
            user=request.user,
            savings=savings,
            code=code
        )

        print("WITHDRAWAL OTP:", code)  # Replace with email/SMS later

        return Response({"message": "OTP sent"}, status=200)


# --------------------------------------------------------
# VERIFY OTP & WITHDRAW (APPLY INTEREST BEFORE WITHDRAW)
# --------------------------------------------------------
class WithdrawSavingsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, savings_id):
        otp = request.data.get("otp")

        if not otp:
            return Response({"error": "OTP is required"}, status=400)

        try:
            savings = Savings.objects.get(id=savings_id, user=request.user)
        except Savings.DoesNotExist:
            return Response({"error": "Savings not found"}, status=404)

        # Apply interest before withdrawal
        savings = apply_interest(savings)

        # Verify lock status
        if not savings.can_withdraw():
            return Response({"error": "Savings is still locked"}, status=400)

        valid, msg = verify_otp(request.user, savings, otp)
        if not valid:
            return Response({"error": msg}, status=400)

        # Release funds
        savings.is_released = True
        savings.released_at = timezone.now()
        savings.save()

        # Log withdrawal
        SavingsTransaction.objects.create(
            savings=savings,
            type="withdrawal",
            amount=savings.amount,
            note="Savings withdrawal approved"
        )

        # Update goal just in case
        savings = update_goal_status(savings)

        return Response(
            {"message": "Withdrawal successful!", "amount": savings.amount},
            status=200
        )

# --------------------------------------------------------
# ACTIVITY HISTORY
# --------------------------------------------------------
class SavingsActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tx = SavingsTransaction.objects.filter(
            savings__user=request.user
        ).order_by("-created_at")

        return Response(
            SavingsTransactionSerializer(tx, many=True).data,
            status=200
        )


# ========================================================
# 🔵 H20 STEP 3 — FLEXIBLE DEPOSIT ANYTIME
# ========================================================
class AddSavingsDepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        savings_id = request.data.get("savings_id")
        amount = request.data.get("amount")
        note = request.data.get("note", "Additional deposit")

        if not savings_id:
            return Response({"error": "savings_id is required"}, status=400)

        if not amount:
            return Response({"error": "amount is required"}, status=400)

        try:
            amount = float(amount)
        except:
            return Response({"error": "Invalid amount"}, status=400)

        if amount <= 0:
            return Response({"error": "Amount must be greater than 0"}, status=400)

        try:
            savings = Savings.objects.get(id=savings_id, user=request.user)
        except Savings.DoesNotExist:
            return Response({"error": "Savings not found"}, status=404)

        # ADD TO MAIN BALANCE
        savings.amount += amount
        savings.save()

        # LOG TRANSACTION
        SavingsTransaction.objects.create(
            savings=savings,
            type="deposit",
            amount=amount,
            note=note
        )

        return Response({
            "message": "Deposit added successfully!",
            "new_balance": savings.amount,
            "savings": SavingsSerializer(savings).data
        }, status=200)

