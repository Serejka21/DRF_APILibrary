from enum import Enum

from django.core.validators import MinValueValidator
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=60)
    author = models.CharField(max_length=60, blank=True)
    cover = models.CharField(
        max_length=60, choices=Enum('Cover', ['HARD', 'SOFT'])
    )
    inventory = models.IntegerField(
        validators=[MinValueValidator(1)],
    )
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)
