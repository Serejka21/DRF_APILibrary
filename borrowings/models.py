from django.db import models


class Borrowing(models.Model):
    borrow_date = models.DateTimeField()
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField()
    book = models.OneToOneField("Book")
    user = models.ForeignKey("User")
