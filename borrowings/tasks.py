import requests

from celery import shared_task

from DRF_API_Library import settings


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
