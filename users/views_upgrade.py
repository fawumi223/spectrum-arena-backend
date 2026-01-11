from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import User

# import the simulated Providus helper (create this file as described previously)
from .providus_service import create_providus_payment_reference


class UpgradePlanView(APIView):
    """
    Step 1 — Initialize upgrade via Providus (simulated for now).
    Requires authenticated user (JWT).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_type = request.data.get("plan_type", "").upper()
        valid_plans = {"STANDARD": 4999, "PREMIUM": 9999}

        if plan_type not in valid_plans:
            return Response(
                {"error": "Invalid plan. Choose 'STANDARD' or 'PREMIUM'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        amount = valid_plans[plan_type]

        # Simulate Providus payment initialization
        payment_data = create_providus_payment_reference(
            amount=amount,
            customer_name=user.full_name,
            customer_email=user.email or "noemail@spectrumarena.com",
        )

        return Response(
            {
                "message": f"Payment initialized for {plan_type} plan",
                "plan_type": plan_type,
                "payment_reference": payment_data.get("reference"),
                "payment_link": payment_data.get("payment_link"),
                "amount": amount,
            },
            status=status.HTTP_200_OK,
        )


class ProvidusWebhookView(APIView):
    """
    Step 2 — Providus Webhook to confirm payment & auto-upgrade user.
    This endpoint should be public (Providus will post to it). In production you should:
      - verify a signature or secret header from Providus
      - restrict IPs if provided by Providus
      - use HTTPS and basic auth / shared secret validation
    """
    # intentionally no authentication: called by external provider
    def post(self, request):
        data = request.data
        # Log for debugging in dev
        print("📩 Providus Webhook Data:", data)

        payment_status = data.get("status", "failed")
        customer = data.get("customer", {})
        customer_email = customer.get("email")
        try:
            amount = float(data.get("amount", 0))
        except (TypeError, ValueError):
            amount = 0.0

        if payment_status != "success":
            return Response({"message": "Payment not successful"}, status=400)

        if not customer_email:
            return Response({"message": "Missing customer email"}, status=400)

        try:
            user = User.objects.get(email=customer_email)

            # Map amount to plan
            if amount == 4999:
                plan = "STANDARD"
            elif amount == 9999:
                plan = "PREMIUM"
            else:
                plan = "BASIC"

            user.update_plan(plan)
            return Response(
                {"message": f"{plan} plan activated for {user.full_name}"},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

