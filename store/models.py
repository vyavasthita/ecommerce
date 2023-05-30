from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Collection(models.Model):
    ELECTRONIC = 'Elec'
    FOOD = 'Food'
    FASHION = 'Fa'
    GROCERY = 'Gro'
    SPORTS = 'Spo'
    BOOKS = 'Bo'
    ENTERTAINMENT = 'Ent'

    COLLECTION_CHOICES = [
        (ELECTRONIC, 'Electronics',),
        (FOOD, 'Food',),
        (FASHION, 'Fashion',),
        (GROCERY, 'Grocery',),
        (SPORTS, 'Sports',),
        (BOOKS, 'Books',),
        (ENTERTAINMENT, 'Entertainmaint',),
    ]
    name = models.CharField(max_length=30, choices=COLLECTION_CHOICES, unique=True)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=50)
    price = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return self.name

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory')
    total_quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    available_quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return f"{self.product} with {self.available_quantity} quantity"

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
                             on_delete=models.CASCADE, 
                             null=True, blank=True)

    def __str__(self) -> str:
        if self.user is not None:
            return f"Cart No ({self.id}) by {self.user.first_name} at {self.created_at.strftime('%m/%d/%Y, %H:%M:%S')}"
        else:
            return f"Cart ({self.id}) by Anonymous created at {self.created_at.strftime('%m/%d/%Y, %H:%M:%S')}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartitems')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)])

    def __str__(self) -> str:
        if self.cart.user is not None:
            return f"Items added for {self.cart.user.first_name} for Cart No {self.cart.id}"
        else:
            return f"Items added for Annonymous"
        
    class Meta:
        unique_together = [['cart', 'product']]
    
class Order(models.Model):
    UNSUCCESSFULL = 'unsucc'
    SUCCESSFULL = 'succ'

    PAYMENT_STATUS_CHOICES = [
        (UNSUCCESSFULL, 'Unsuccessfull',),
        (SUCCESSFULL, 'Successfull',),
    ]

    INPROGRESS = 'inp'
    COMPLETED = 'comp'
    CANCELLED = 'can'

    ORDER_STATUS_CHOICES = [
        (INPROGRESS, 'Inprogress',),
        (COMPLETED, 'Completed',),
        (CANCELLED, 'Cancelled',),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems')
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)])