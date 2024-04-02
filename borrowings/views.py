import datetime

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        borrowing = Borrowing.objects.get(pk=serializer["id"].value)
        borrowing.book.inventory -= 1
        borrowing.book.save()

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

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

    @action(
        methods=["GET"],
        detail=True,
        url_path="return",
        permission_classes=[IsAdminUser]
    )
    def return_book(self, request, pk):

        with transaction.atomic():
            borrowing = Borrowing.objects.get(pk=pk)

            data = {"error": "This borrowing is already closed"}

            if borrowing.actual_return_date:
                return Response(
                    data=data,
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = BorrowingReturnSerializer(borrowing)

            borrowing.actual_return_date = datetime.datetime.now()
            borrowing.save()

            borrowing.book.inventory += 1
            borrowing.book.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
