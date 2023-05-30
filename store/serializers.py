from rest_framework import serializers
from .models import Collection, Product, Inventory, Cart, CartItem, Order, OrderItem


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'name']

class CollectionForInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['name']

class ProductSerializer(serializers.ModelSerializer):
    collection = CollectionSerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'collection']

class ProductForInventorySerializer(serializers.ModelSerializer):
    collection = CollectionForInventorySerializer()

    class Meta:
        model = Product
        fields = ['name', 'collection']

class ProductForCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']

class InventorySerializer(serializers.ModelSerializer):
    product = ProductForInventorySerializer()

    class Meta:
        model = Inventory
        fields = ['id', 'product', 'total_quantity', 'available_quantity']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductForCartItemSerializer()
    item_price = serializers.SerializerMethodField()

    def get_item_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.price
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_price']

class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'quantity']

class DeleteCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id']

class CartSerializer(serializers.ModelSerializer):
    cartitems = CartItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=False)
    total_cart_value = serializers.SerializerMethodField()

    def get_total_cart_value(self, cart: Cart):
        return sum([cart_item.quantity * cart_item.product.price for cart_item in cart.cartitems.all()])
    
    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'user', 'cartitems', 'total_cart_value']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductForCartItemSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=False)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'user', 'payment_status', 'order_status', 'orderitems']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'payment_status']