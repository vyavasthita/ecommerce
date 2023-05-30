from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import CollectionViewSet, ProductViewSet, InventoryViewSet, \
        CartViewSet, CartItemViewSet, OrderItemViewSet, OrderViewSet


router = DefaultRouter()

router.register('collection', CollectionViewSet)
router.register('product', ProductViewSet)
router.register('inventory', InventoryViewSet)
router.register('cart', CartViewSet, basename='cart')
router.register('order', OrderViewSet, basename='order')

# router.register('cartitems', CartItemViewSet, basename='cartitems')

cart_router = routers.NestedDefaultRouter(router, 'cart', lookup='cart')
cart_router.register('cartitems', CartItemViewSet, basename='cart-items')

order_router = routers.NestedDefaultRouter(router, 'order', lookup='order')
order_router.register('orderitems', OrderItemViewSet, basename='order-items')

urlpatterns = router.urls + cart_router.urls + order_router.urls