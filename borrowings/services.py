from django.http import HttpRequest
from django.db.models.query import QuerySet


def filtering(
        queryset: QuerySet, request: HttpRequest
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
