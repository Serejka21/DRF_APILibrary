import stripe
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentSuccessSerializer
)
from payment.utils.services import PaymentService


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(borrowing__user=self.request.user)

    @action(
        methods=["GET"],
        detail=False,
        url_path="success",
        url_name="success"
    )
    def payment_success(self, request):
        """
        Endpoint to handle successful payment confirmation.

        This endpoint is called when a payment is successfully confirmed.
        It validates the session ID received from the query parameters,
        marks the payment as paid, and returns a success message.

        Args:
        - request: HTTP request object.

        Returns:
        - Response with a success message if the payment is
        successfully confirmed.
          Otherwise, returns an error message if there's an
          issue with the payment confirmation.
        """
        serializer = PaymentSuccessSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        session_id = serializer.validated_data.get("session_id")

        try:
            PaymentService().set_paid_status(session_id)
            return Response(
                {"message": f"Thanks for your payment, {request.user.email}!"},
                status=status.HTTP_200_OK
            )
        except stripe.error.InvalidRequestError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=["GET"],
        detail=False,
        url_path="cancel",
        url_name="cancel"
    )
    def payment_cancel(self, request):
        """
        Endpoint to inform the user that payment can be made later.

        This endpoint should be accessed when the user
        decides to cancel the payment.
        It informs the user that the payment can be paid a bit later,
        but the session is available for only 24 hours.

        Args:
        - request: HTTP request object.

        Returns:
        - Response with a message informing the user
        about the payment cancelation.
        """
        message = (
            "Your payment can be paid later, "
            "but the session is available for only 24 hours."
        )
        return Response({"message": message}, status=status.HTTP_200_OK)
