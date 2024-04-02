import os
from decimal import Decimal

import stripe

from payment.models import Borrowing, Payment


class PaymentService:
    FINE_MULTIPLIER = 2
    STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")
    SUCCESS_URL = (
        "http://localhost:8000/api/library/"
        "payments/success?session_id={CHECKOUT_SESSION_ID}"
    )
    CANCEL_URL = "http://localhost:8000/api/library/payments/cancel/"

    @classmethod
    def _create_stripe_session(
            cls,
            borrowing: Borrowing,
            money_to_pay: Decimal
    ):
        """
        Create a Stripe checkout session for the given borrowing.

        Args:
        - borrowing: Borrowing object representing the transaction.
        - money_to_pay: The total amount to be paid for the borrowing.

        Returns:
        - session: Stripe checkout session object.
        """
        stripe.api_key = cls.STRIPE_API_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": borrowing.book.title,
                        },
                        "unit_amount": int(money_to_pay) * 100,
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=cls.SUCCESS_URL,
            cancel_url=cls.CANCEL_URL,
        )

        return session

    @classmethod
    def create_payment(cls, borrowing: Borrowing) -> None:
        """
        Create a new payment for the given borrowing.

        This method calculates the amount to be paid based on the borrowing's
        duration and daily fee, creates a Stripe checkout session, and then
        creates a new Payment object with the relevant details.

        Args:
        - borrowing: Borrowing object representing the transaction.

        Returns:
        - None
        """
        days_borrowed = borrowing.expected_return_date - borrowing.borrow_date
        money_to_pay = days_borrowed.days * borrowing.book.daily_fee
        session = cls._create_stripe_session(borrowing, money_to_pay)

        Payment.objects.create(
            status="PENDING",
            payment_type="PAYMENT",
            borrowing=borrowing,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=money_to_pay
        )

    @classmethod
    def calculate_fine(cls, borrowing: Borrowing) -> None:
        """
        Calculate the fine for a borrowing.

        Parameters:
            borrowing (Borrowing): The Borrowing object
            for which the fine is being calculated.

        Returns:
            None

        Applies the fine multiplier FINE_MULTIPLIER to the number of
        overdue days, multiplied by the daily fee for the book,
        to get the total fine amount. Creates a payment with type "FINE"
        for tracking the fine in the Stripe system.
        """

        overdue_days = (
            borrowing.actual_return_date - borrowing.expected_return_date
        ).days
        daily_fee = borrowing.book.daily_fee
        fine_amount = overdue_days * daily_fee * cls.FINE_MULTIPLIER
        session = cls._create_stripe_session(borrowing, fine_amount)

        Payment.objects.create(
            status="PENDING",
            payment_type="FINE",
            borrowing=borrowing,
            session_id=session.id,
            session_url=session.url,
            money_to_pay=fine_amount,
        )

    @classmethod
    def set_paid_status(cls, session_id):
        """
        Set the payment status to PAID for the given session ID.

        This method retrieves the session details from Stripe
        using the session ID, retrieves the corresponding
        payment object from the database, and updates the payment status
        to PAID.

        Args:
        - session_id: The ID of the Stripe checkout session.

        Returns:
        - None
        """
        stripe.api_key = cls.STRIPE_API_KEY
        stripe.checkout.Session.retrieve(session_id)
        payment = Payment.objects.get(session_id=session_id)
        payment.status = Payment.Status.PAID
        payment.save()
