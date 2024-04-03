import requests

from decimal import Decimal
from celery import shared_task

from DRF_API_Library import settings


TOKEN = settings.TOKEN
CHAT_ID = settings.CHAT_ID

# add message at the end of url
URL = (f"https://api.telegram.org/bot{TOKEN}"
       f"/sendMessage?chat_id={CHAT_ID}&text=")


@shared_task()
def send_success_payment_notification(
    borrowing_id: int,
    user_email: str,
    money_to_pay: Decimal
) -> None:
    """Use telegram API to send notification"""
    message = (f"Customer: {user_email}\n"
               f"successful payed {money_to_pay} "
               f"for borrowing with id:{borrowing_id}.\n")
    requests.post(f"{URL}{message}")
