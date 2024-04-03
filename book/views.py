from rest_framework import viewsets, mixins, status
from rest_framework.exceptions import ValidationError

from book.models import Book
from book.permissions import IsAdminOrReadOnly
from book.serializers import BookSerializer


class BookViewSet(
    viewsets.ModelViewSet
):
    """ViewSet for Model book"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def perform_destroy(self, instance):
        """Protection of the book from destroy if it has min 1 borrowing"""
        if instance.borrowings.count() == 0:
            instance.delete()

        else:
            raise ValidationError(
                "You cannot delete this book. Book has borrowings",
                code=status.HTTP_403_FORBIDDEN
            )
