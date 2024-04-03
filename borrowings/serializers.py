from rest_framework import serializers

from book.serializers import BookSerializer
from borrowings.models import Borrowing
from payment.serializers import PaymentBorrowingSerializer
from borrowings.services import borrowing_create_validation
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    """Borrowing serializer with all fields."""

    book = serializers.StringRelatedField()
    user_email = serializers.CharField(
        source="user.email", read_only=True
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user_email",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    """Borrowing create serializer."""

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
        read_only_fields = ("borrow_date", "actual_return_date", "user")

    def validate(self, attrs):
        validated_attrs = borrowing_create_validation(attrs)

        return validated_attrs


class BorrowingDetailSerializer(BorrowingSerializer):
    """Borrowing detail serializer."""

    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    payments = PaymentBorrowingSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")
