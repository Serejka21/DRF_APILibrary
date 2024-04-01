from rest_framework import viewsets, mixins

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
