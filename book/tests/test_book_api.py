from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from book.models import Book
from book.serializers import BookSerializer
from borrowings.models import Borrowing

BOOK_URL = reverse("book:book-list")


def sample_book(**params):
    """Create a sample book for tests"""
    defaults = {
        "title": "Sample book",
        "author": "Same author",
        "cover": "HARD",
        "inventory": 1,
        "daily_fee": "4.64"
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(book_id):
    return reverse("book:book-detail", args=[book_id])


class UnauthenticatedBookApiTests(TestCase):
    """Tests for unauthenticated user that can enable to book list"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthenticatedBookApiTests(TestCase):
    """Tests for Authenticated user that can enable to book (list/detail)"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_books(self):
        sample_book()
        sample_book()

        res = self.client.get(BOOK_URL)

        books = Book.objects.order_by("id")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        """Test for Authenticated user that can`t create book"""
        payload = {
            "title": "Sample book",
            "author": "Same author",
            "cover": "HARD",
            "inventory": 1,
            "daily_fee": Decimal("4.64")
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    """Tests for user with admin permission that can create/delete book"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.payload = {
            "title": "Sample book",
            "author": "Same author",
            "cover": "HARD",
            "inventory": 1,
            "daily_fee": Decimal("4.64")
        }
        self.book = Book.objects.create(**self.payload)
        self.borrowing = Borrowing.objects.create(
            borrow_date=timezone.now(),
            expected_return_date=timezone.now() + timezone.timedelta(days=7),
            book=self.book,
            user=self.user
        )

    def test_create_book(self):
        res = self.client.post(BOOK_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])
        for key in self.payload.keys():
            self.assertEqual(self.payload[key], getattr(book, key))

    def test_delete_book_without_borrowings(self):
        res = self.client.post(BOOK_URL, self.payload)
        book = Book.objects.get(id=res.data["id"])

        delete_res = self.client.delete(reverse('book:book-detail', args=[book.id]))
        self.assertEqual(delete_res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_book_with_borrowings(self):

        delete_res = self.client.delete(reverse('book:book-detail', args=[self.book.id]))
        self.assertEqual(delete_res.status_code, status.HTTP_400_BAD_REQUEST)
