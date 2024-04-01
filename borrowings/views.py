import datetime

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from borrowings.services import filtering


class BorrowingViewSet(viewsets.ModelViewSet):
    """Borrowing view set with implemented filtering
     by user_id or is_active status and custom action return."""

    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer()

    def get_queryset(self):
        return filtering(self.queryset, self.request)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["GET"], detail=True, url_path="return")
    def return_book(self, request, pk):

        with transaction.atomic():
            borrowing = Borrowing.objects.get(pk=pk)

            borrowing.actual_return_date = datetime.datetime.now()
            borrowing.save()

            serializer = BorrowingReturnSerializer(borrowing)

            return Response(serializer.data, status=status.HTTP_200_OK)
