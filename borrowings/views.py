from rest_framework import viewsets

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingDetailSerializer
from borrowings.services import filtering


class BorrowingViewSet(viewsets.ModelViewSet):
    """Borrowing view set with implemented filtering by user_id or is_active status."""

    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer()

    def get_queryset(self):
        if self.request.user.is_staff:
            return filtering(self.queryset, self.request)

        return filtering(
            self.queryset.filter(user=self.request.user),
            self.request
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)