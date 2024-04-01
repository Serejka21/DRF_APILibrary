from django.db import models
from django.conf import settings

from book.models import Book


class Borrowing(models.Model):
    """Borrowing model."""

    borrow_date = models.DateTimeField()
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    book = models.OneToOneField(Book, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
