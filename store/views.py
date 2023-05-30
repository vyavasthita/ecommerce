from django.shortcuts import render, get_object_or_404
from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .serializers import CollectionSerializer, \
    ProductSerializer, InventorySerializer, \
        CartSerializer, CartItemSerializer, \
            AddCartItemSerializer, UpdateCartItemSerializer, \
            DeleteCartItemSerializer, OrderItemSerializer, \
                OrderSerializer, UpdateOrderSerializer
from .models import Collection, Product, Inventory, Cart, CartItem, Order, OrderItem
from .signals import delete_cart_for_an_order


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]
    
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]

class InventoryViewSet(ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer

    def get_permissions(self):
        if self.request.method in ['GET', 'POST', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_queryset(self):
        if self.request.method == 'GET':
            if self.request.user.is_staff:
                return Cart.objects.all()
            else:
                return Cart.objects.filter(user_id = self.request.user.id)

    def create(self, request, *args, **kwargs):
        user_id = self.request.user.id

        if Cart.objects.filter(user_id=user_id).exists():
            return Response({'error': 'Duplicate cart can not be created.'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=user_id)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        user_id = request.user.id

        if not Cart.objects.filter(user_id = user_id).exists():
            return Response({'error': 'User does not have any cart associated with it.'},
                            status=status.HTTP_404_NOT_FOUND)
        
        Cart.objects.filter(user_id = user_id).delete()
        return Response(status=status.HTTP_200_OK)

class CartItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PUT':
            return UpdateCartItemSerializer
        elif self.request.method == 'DELETE':
            return DeleteCartItemSerializer
        
        return CartItemSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_id=kwargs['cart_pk']

        product_id = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        inventory = Inventory.objects.get(product_id = product_id)

        if quantity > inventory.available_quantity:
            quantity = inventory.available_quantity

        with transaction.atomic():
            try:
                # Update request if no exception is thrown, else create request.
                cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
                cart_item.quantity += quantity
                serializer.validated_data['quantity'] = quantity
                cart_item.save()                
            except CartItem.DoesNotExist:
                # Create request                
                CartItem.objects.create(cart_id = cart_id, **serializer.validated_data)

            inventory.available_quantity -= quantity
            inventory.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        serializer = DeleteCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item = CartItem.objects.get(pk=kwargs['pk'])
        quantity = cart_item.quantity
        product_id = cart_item.product

        # Update inventory
        inventory = Inventory.objects.get(product_id=product_id)
        inventory.available_quantity += quantity
        inventory.save()

        # delete cart item
        cart_item.delete()
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():        
            cart_item = CartItem.objects.get(pk=kwargs['pk'])
            inventory = Inventory.objects.get(product_id = cart_item.product_id)

            quantity = serializer.validated_data['quantity']

            if quantity > inventory.available_quantity:
                quantity = inventory.available_quantity

            cart_item.quantity += quantity
            serializer.validated_data['quantity'] = quantity
            cart_item.save()

            inventory.available_quantity -= quantity
            inventory.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)        
    
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    
class OrderViewSet(ModelViewSet):
    def get_permissions(self):
        if self.request.method in ['DELETE', 'PUT', 'PATCH']:
            return [IsAdminUser()]
        
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return UpdateOrderSerializer
        
        return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        
        return Order.objects.filter(user_id = self.request.user.id)
    
    def create(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = request.user.id

        with transaction.atomic():
            order = Order.objects.create(user_id = user_id, 
                            payment_status = serializer.validated_data['payment_status'],
                            order_status = serializer.validated_data['order_status']
                    )

            # Fetch cart for given user
            cart = Cart.objects.get(user_id = user_id)

            order_items = [
                    OrderItem(
                        order = order, 
                        product = cart_item.product, 
                        quantity = cart_item.quantity
                    ) 
                    for cart_item in CartItem.objects.filter(cart = cart.id)
            ]

            OrderItem.objects.bulk_create(order_items)
            # Cart.objects.filter(pk=cart.id).delete()
        
        delete_cart_for_an_order.send(sender='create_order', cart_id = cart.id)
        
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
