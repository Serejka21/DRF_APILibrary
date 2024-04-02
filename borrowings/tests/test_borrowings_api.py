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
        "user": params["user"],
        "actual_return_date": None
    }

    defaults.update(params)

    return Borrowing.objects.create(**defaults)


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

        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_borrowings_by_is_active(self):
        active_borrowing = sample_borrowing(user=self.user)
        inactive_borrowing = sample_borrowing(
            user=self.user, actual_return_date="2024-06-07"
        )

        res = self.client.get(
            BORROWING_URL, {"is_active": "true"}
        )

        active_serializer = BorrowingSerializer(active_borrowing)
        inactive_serializer = BorrowingSerializer(inactive_borrowing)

        self.assertIn(active_serializer.data, res.data["results"])
        self.assertNotIn(inactive_serializer.data, res.data["results"])

    def test_borrowing_create(self):

        book = Book.objects.create(
            title="testBook",
            author="testAuthor",
            inventory=5,
            daily_fee=2
        )

        now = timezone.now()
        now_plus_one_day = now + datetime.timedelta(days=1, minutes=1)

        payload = {
            "expected_return_date": now_plus_one_day,
            "book": book.id,
            "user": self.user.id,
        }

        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    def test_can_not_borrow_book_less_than_one_day(self):

        book = Book.objects.create(
            title="testBook",
            author="testAuthor",
            inventory=5,
            daily_fee=2
        )

        now = timezone.now()
        now_plus_one_day = now + datetime.timedelta(hours=23, minutes=59)

        payload = {
            "expected_return_date": now_plus_one_day,
            "book": book.id,
            "user": self.user.id,
        }

        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_filter_borrowings_by_user_id(self):
        user2 = get_user_model().objects.create_user(
            "user2@email.com", "testpass_user2"
        )

        borrowing1 = sample_borrowing(user=self.user)
        borrowing2 = sample_borrowing(user=user2)

        res = self.client.get(
            BORROWING_URL, {"user_id": "1"}
        )

        active_serializer = BorrowingSerializer(borrowing1)
        inactive_serializer = BorrowingSerializer(borrowing2)

        self.assertIn(active_serializer.data, res.data["results"])
        self.assertNotIn(inactive_serializer.data, res.data["results"])
