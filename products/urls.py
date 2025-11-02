from django.urls import include, path
from rest_framework import routers

from .views import ProductViewSet, OrderViewSet, TransactionSet, ProductAdminViewSet,ProductKeyViewSet,OrderAdminViewSet,NotificationViewSet

app_name = "products"

router = routers.DefaultRouter()
router.register("products", ProductViewSet)
router.register("admin-products", ProductAdminViewSet)
router.register("admin-products-keys", ProductKeyViewSet)
router.register("order", OrderAdminViewSet)
router.register("notifications", NotificationViewSet)


router.register("product/purchase", OrderViewSet)
router.register("transaction/verify", TransactionSet)


urlpatterns = [
    path("", include(router.urls)),
]
