from collections import OrderedDict
import datetime
from django.utils import timezone

from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request


def filtering(
        queryset: QuerySet, request: Request
) -> QuerySet:
    user_id = request.query_params.get("user_id")
    is_active = request.query_params.get("is_active")

    if not request.user.is_staff:
        queryset = queryset.filter(user=request.user)

    if user_id:
        queryset = queryset.filter(user_id=user_id)

    if is_active is not None:
        if is_active.lower() == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)

        if is_active.lower() == "false":
            queryset = queryset.filter(actual_return_date__isnull=False)

    return queryset


def borrowing_create_validation(attrs: OrderedDict) -> OrderedDict:
    expected_return_date = attrs["expected_return_date"]

    now = timezone.now()
    now_plus_one_day = now + datetime.timedelta(days=1)

    if expected_return_date < now_plus_one_day:
        raise ValidationError(
            "Borrow time can`t be lass than one day",
            code=status.HTTP_403_FORBIDDEN
        )

    book_inventory = attrs["book"].inventory

    if book_inventory <= 0:
        raise ValidationError(
            "Sorry but all such books were taken away",
            code=status.HTTP_403_FORBIDDEN
        )

    return attrs
