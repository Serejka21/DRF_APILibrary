from rest_framework import serializers

from borrowings.models import Borrowing


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


class BorrowingDetailSerializer(BorrowingSerializer):
    """Borrowing detail serializer."""

    pass


