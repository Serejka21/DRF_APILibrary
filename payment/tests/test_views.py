import datetime
from unittest.mock import patch

import stripe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from borrowings.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentSerializer

PAYMENT_URL = reverse("payment:payment-list")
PAYMENT_SUCCESS_URL = reverse("payment:payment-success")
PAYMENT_CANCEL_URL = reverse("payment:payment-cancel")


def detail_url(payment_id):
    """Helper function to return payment detail URL"""
    return reverse("payment:payment-detail", args=[payment_id])


class UnauthenticatedPaymentApiTests(TestCase):
    """
    Tests for checking the functionality
    of the payment API without authentication.
    """
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Checks that authentication is required to access the payment API.
        """
        response = self.client.get(PAYMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTests(TestCase):
    """
    Tests for checking the functionality
    of the payment API with authentication.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345"
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=(
                datetime.date.today() + datetime.timedelta(days=3)
            ),
            book=Book.objects.create(
                title="Test book",
                daily_fee=3.33,
                inventory=1
            ),
            user=self.user
        )
        self.payment = Payment.objects.create(borrowing=self.borrowing)
        self.client.force_authenticate(self.user)

    def test_payment_list(self):
        """
        Test retrieving a list of payments.
        """
        response = self.client.get(PAYMENT_URL)
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_payment(self):
        """
        Test retrieving a specific payment.
        """
        response = self.client.get(detail_url(self.payment.id))
        serializer = PaymentSerializer(self.payment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_payment_forbidden(self):
        """
        Test that creating a payment is not allowed.
        """
        payload = {
            "borrowing": self.borrowing,
        }
        response = self.client.post(PAYMENT_URL, payload)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @patch("payment.views.PaymentService")
    def test_payment_success_with_valid_data(self, mock_payment_service):
        """
        Test successful payment confirmation with valid data.

        Verifies that the payment is successfully confirmed
        when valid session ID is provided.
        """
        session_id = "mock_session_id"

        mock_payment_service.return_value.set_paid_status.return_value = None

        response = self.client.get(
            PAYMENT_SUCCESS_URL,
            {"session_id": session_id}
        )
        (
            mock_payment_service
            .return_value
            .set_paid_status
            .assert_called_once_with(session_id)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {"message": f"Thanks for your payment, {self.user.email}!"}
        )

    @patch("payment.utils.services.PaymentService.set_paid_status")
    def test_payment_success_with_invalid_data(self, mock_set_status_as_paid):
        """
        Test payment confirmation with invalid data.

        Verifies that an error is returned when invalid data is provided.
        """
        mock_set_status_as_paid.side_effect = (
            stripe.error.InvalidRequestError("Invalid request", None)
        )
        query_params = {"session_id": "test_session_id"}

        res = self.client.get(PAYMENT_SUCCESS_URL, data=query_params)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["error"], "Invalid request")

    def test_payment_cancel(self):
        """
        Test payment cancellation.

        Verifies that a message is returned for payment cancellation.
        """
        response = self.client.get(PAYMENT_CANCEL_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "message": "Your payment can be paid later, "
                           "but the session is available for only 24 hours."
            }
        )


class AdminPaymentApiTests(TestCase):
    """
    Test cases for the Payment API endpoints with admin privileges.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test_admin@test.com",
            password="admintest123"
        )
        self.client.force_authenticate(self.user)
        self.borrowing = Borrowing.objects.create(
            expected_return_date=(
                datetime.date.today() + datetime.timedelta(days=3)
            ),
            book=Book.objects.create(
                title="Test Admin Book",
                daily_fee=2.11,
                inventory=2
            ),
            user=self.user
        )
        self.payment = Payment.objects.create(borrowing=self.borrowing)

    def test_update_payment_not_allowed(self):
        """
        Test that updating a payment is not allowed.
        """
        payload = {"borrowing": self.borrowing}

        response = self.client.put(detail_url(self.payment.id), payload)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_payment_not_allowed(self):
        """
        Test that deleting a payment is not allowed.
        """
        response = self.client.delete(detail_url(self.payment.id))

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
