from rest_framework import viewsets

from borrowings.models import Borrowing


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()

