from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowings.tasks import send_borrowing_created_notification
from borrowings.models import Borrowing


@receiver(
    post_save,
    sender=Borrowing,
    dispatch_uid="post_save_signal_processed"
)
def send_borrowing_created_message(sender, instance, created, **kwargs):
    """Handle creation of Borrowing"""
    try:
        if created:
            send_borrowing_created_notification.delay(
                instance.id,
                instance.user.email,
                instance.borrow_date,
                instance.expected_return_date,
            )
    except Exception as e:
        print("Error sending created borrowing notification!")
        print(e)
