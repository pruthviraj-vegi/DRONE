from customers.models import Member
from suppliers.models import Supplier
from base.stringProcess import StringProcessor
from django.http import JsonResponse
from inventory.models import Inventory


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


class Suggestion:
    def __init__(self, request=None):
        self.request = request

    def get_address(self):
        customer_address = Member.objects.all().values_list("address", flat=True)
        supplier_address = Supplier.objects.all().values_list("address", flat=True)
        address = list(set(list(customer_address) + list(supplier_address)))
        address = [StringProcessor(addr).title for addr in address]
        print(address)
        return JsonResponse(address, safe=False)

    def get_company_name(self, name=None):
        data = Inventory.objects.all()
        data_list = []
        if name == "company_name":
            data_list = data.values_list("company_name", flat=True)
        elif name == "part_name":
            data_list = data.values_list("part_name", flat=True)
        else:
            return JsonResponse([], safe=False)

        data_list = list(set(data_list))
        data_list = [StringProcessor(name).title for name in data_list]
        return JsonResponse(data_list, safe=False)
