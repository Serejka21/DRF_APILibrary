import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from book.models import Book
from borrowings.models import Borrowing
from payment.models import Payment


def sample_payment(**params):
    """Helper function for creating a sample Payment instance."""
    borrowing = Borrowing.objects.create(
        expected_return_date=datetime.date.today() + datetime.timedelta(days=3),
        book=Book.objects.create(
            title="Test book",
            daily_fee=3.33,
            inventory=1
        ),
        user=get_user_model().objects.create_user(
            email="test@test.com", password="test12345"
        )
    )
    defaults = {"borrowing": borrowing}
    defaults.update(params)
    return Payment.objects.create(**defaults)


class PaymentModelTest(TestCase):

    def setUp(self):
        self.payment = sample_payment()

    def test_payment_str(self):
        """
        Test for the string representation of the Payment model.

        Checks that the string representation of a Payment instance matches the expected format.
        """
        self.assertEqual(
            str(self.payment),
            f"Payment ID: {self.payment.id} - Status: {self.payment.status}"
        )
