from django.contrib import admin
from .models import Collection, Product, Inventory, Cart, CartItem


admin.site.register(Collection)
admin.site.register(Product)
admin.site.register(Inventory)
admin.site.register(Cart)
admin.site.register(CartItem)
