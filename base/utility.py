def get_basic_data(request):
    search_query = request.GET.get("search", "")
    limit = request.GET.get("limit", 30)
    start = request.GET.get("start", 0)
    sort_column = request.GET.get("sort_column", "id")
    sort_order = request.GET.get("sort_order", "desc")

    sort_column = f"-{sort_column}" if sort_order == "desc" else sort_column

    return {
        "search_query": search_query,
        "limit": int(limit),
        "start": int(start),
        "sort_column": sort_column,
        "sort_order": sort_order,
    }
