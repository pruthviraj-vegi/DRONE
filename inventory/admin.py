from django.contrib import admin
from .models import Inventory, StockTransaction

# Register your models here.
admin.site.register(Inventory)
admin.site.register(StockTransaction)
