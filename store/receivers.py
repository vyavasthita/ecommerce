from django.dispatch import receiver
from .signals import delete_cart_for_an_order
from .models import Cart


@receiver(delete_cart_for_an_order)
def delete_cart(sender, cart_id, **kwargs):
    Cart.objects.filter(pk=cart_id).delete()