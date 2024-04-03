import requests

from datetime import timedelta

from celery import shared_task

from DRF_API_Library import settings
from borrowings.models import Borrowing


TOKEN = settings.TOKEN
CHAT_ID = settings.CHAT_ID

# add message at the end of url
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text="


@shared_task()
def send_borrowing_created_notification(
    borrow_id: str,
    user_email: str,
    borrow_date,
    expected_return_date,
) -> None:
    """Use telegram API to send notification"""
    message = (f"Borrowing {borrow_id}"
               f" was created by {user_email}.\n"
               f"Borrow date: {borrow_date}.\n"
               f"Expected return date: {expected_return_date}")
    requests.post(f"{URL}{message}")


@shared_task()
def send_borrowing_overdue_notification(
    borrow_id: str,
    user_email: str,
    borrow_date,
    expected_return_date,
) -> None:
    """Use telegram API to send notification about borrowing overdue"""
    message = (f"!!!Borrowing {borrow_id}"
               f" is overdue by {user_email}!!!\n"
               f"Borrow date: {borrow_date}.\n"
               f"Expected return date: {expected_return_date}")
    requests.post(f"{URL}{message}")


@shared_task()
def check_borrowings_for_overdue() -> None:
    """Check borrowings for overdue and send notification about borrowings status"""
    overdue_missing = True
    for borrowing in Borrowing.objects.all():
        if borrowing.borrow_date - borrowing.expected_return_date <= timedelta(days=1):
            send_borrowing_overdue_notification.delay(
                borrowing.id,
                borrowing.user.email,
                borrowing.borrow_date,
                borrowing.expected_return_date
            )
            overdue_missing = False

    if overdue_missing:
        message = "No borrowings overdue today!"
        requests.post(f"{URL}{message}")
