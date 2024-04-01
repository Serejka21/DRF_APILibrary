
def filtering(queryset, request):
    user_id = request.query_params.get("user_id")
    is_active = request.query_params.get("is_active")

    if user_id:
        queryset = queryset.filter(user_id=user_id)

    if is_active == True:
        queryset = queryset.filter(actual_return_date__isnull=True)

    if is_active == False:
        queryset = queryset.filter(actual_return_date__isnull=False)

    return queryset