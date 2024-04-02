from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer with all fields."""

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "payment_type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentSuccessSerializer(serializers.Serializer):
    """Payment serializer for success payments."""

    session_id = serializers.CharField(max_length=100)


class PaymentBorrowingSerializer(serializers.ModelSerializer):
    """Payment serializer for borrowing detail page"""

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "payment_type",
            "session_url",
            "money_to_pay"
        )
