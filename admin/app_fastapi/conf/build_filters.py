from django.db.models import Q, CharField, TextField


def auto_search_filters(model, search_values=None, mode="or"):
    """
    جستجوی اتوماتیک روی تمام فیلدهای متنی (CharField, TextField) یک مدل

    :param model: مدل جنگو (مثلاً StoreProduct)
    :param search_values: dict از مقادیر سرچ {"q": "mahdi", "search": "test"}
    :param mode: 'or' یا 'and'
    :return: Q object
    """
    if not search_values:
        return Q()

    # فقط فیلدهای متنی مدل
    text_fields = [
        f.name for f in model._meta.get_fields()
        if isinstance(getattr(f, "field", f), (CharField, TextField))
    ]

    queries = []
    for _, value in (search_values or {}).items():
        if not value:
            continue
        for field in text_fields:
            queries.append(Q(**{f"{field}__icontains": value}))

    if not queries:
        return Q()

    combined = queries[0]
    for q in queries[1:]:
        if mode == "and":
            combined &= q
        else:
            combined |= q

    return combined
