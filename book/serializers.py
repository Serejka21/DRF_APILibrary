from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from book.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
        )

    def validate(self, value):
        if value["inventory"] < 1:
            raise ValidationError(
                "Inventory can`t be less than 1", code=status.HTTP_403_FORBIDDEN
            )
        if value["daily_fee"] <= 0:
            raise ValidationError(
                "Daily fee can`t be less than 0", code=status.HTTP_403_FORBIDDEN
            )
        return value
