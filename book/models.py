from django.db import models


class CoverType(models.TextChoices):
    HARD = "HARD", "Hardcover"
    SOFT = "SOFT", "Softcover"


class Book(models.Model):
    """Model book"""
    title = models.CharField(max_length=60)
    author = models.CharField(max_length=60, blank=True)
    cover = models.CharField(
        max_length=60, choices=CoverType.choices, default="HARD"
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title
