from django.dispatch import receiver, Signal

from payment.tasks import send_success_payment_notification
from payment.models import Payment


successful_payment = Signal()


@receiver(
    successful_payment,
    sender=Payment,
    dispatch_uid="post_save_signal_processed"
)
def send_success_payment_message(sender, instance, created, **kwargs):
    """Handle successful payment"""
    if created:
        try:
            send_success_payment_notification.delay(
                instance.borrowing.id,
                instance.borrowing.user.email,
                instance.money_to_pay
            )
        except Exception as e:
            print("Error sending created borrowing notification!")
            print(e)
