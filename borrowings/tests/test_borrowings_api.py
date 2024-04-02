from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer
from user.models import User

BORROWING_URL = reverse("borrowings:borrowing-list")


def sample_borrowing(**params):
    book = Book.objects.create(
        title="testBook",
        author="testAuthor",
        inventory=5,
        daily_fee=2
    )

    defaults = {
        "expected_return_date": "2024-06-07",
        "book": book,
        "user": params["user"]
    }

    defaults.update(params)

    Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowing(self):

        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data, serializer.data)
