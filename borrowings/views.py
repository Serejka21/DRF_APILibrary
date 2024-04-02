import datetime

from django.db import transaction
from django.shortcuts import redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from borrowings.services import filtering
from payment.utils.services import PaymentService


class BorrowingPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class BorrowingViewSet(viewsets.ModelViewSet):
    """Borrowing view set with implemented filtering
     by user_id or is_active status and custom action return."""

    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer()
    permission_classes = (IsAuthenticated,)
    pagination_class = BorrowingPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.perform_create(serializer)

            borrowing = Borrowing.objects.get(pk=serializer["id"].value)
            borrowing.book.inventory -= 1
            borrowing.book.save()

            PaymentService().create_payment(borrowing)
            session_url = borrowing.payments.last().session_url

            return redirect(session_url)

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
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsAdminUser]
    )
    def return_book(self, request, pk):
        """Custom return_book action"""
        borrowing = Borrowing.objects.get(pk=pk)

        if borrowing.actual_return_date:
            data = {"error": "This borrowing is already closed"}
            return Response(
                data=data,
                status=status.HTTP_403_FORBIDDEN
            )

        with transaction.atomic():
            serializer = BorrowingReturnSerializer(borrowing)

            borrowing.actual_return_date = datetime.datetime.now().date()
            borrowing.save()

            borrowing.book.inventory += 1
            borrowing.book.save()

            if borrowing.actual_return_date > borrowing.expected_return_date:
                PaymentService().calculate_fine(borrowing)
                session_url = borrowing.payments.last().session_url

                return redirect(session_url)

            return Response(serializer.data, status=status.HTTP_200_OK)
