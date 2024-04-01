from django.db import models


class Borrowing(models.Model):
    """Borrowing model."""

    borrow_date = models.DateTimeField()
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    book = models.OneToOneField("Book")  # TODO: remove mock
    user = models.ForeignKey("User")     # TODO: remove mock
