import os
import uuid

from model_utils import Choices

from django.db import models
from imagekit.models import ProcessedImageField
from smart_selects.db_fields import ChainedForeignKey
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.conf import settings

from authentication.models import UserStampedModel
from model_utils.models import TimeStampedModel


# Create your models here.


def get_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    model = instance.__class__._meta
    path = model.verbose_name_plural.lower().replace(" ", "_")
    return os.path.join(path, filename)


def get_upload_path_file(instance, filename):
    name = filename.split(".")[0]
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}_{name}.{ext}"
    model = instance.__class__._meta
    path = model.verbose_name_plural.lower().replace(" ", "_")
    return os.path.join(path, filename)




class Product(UserStampedModel, TimeStampedModel):

    STATUS = Choices(
        ("active", "Active"),
        ("inactive", "Inactive"),
    )

    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    price = models.PositiveIntegerField()
    image = ProcessedImageField(
        upload_to=get_upload_path
    )

    is_deleted = models.BooleanField(default=False)
    status = models.CharField("Status", choices=STATUS,
                              max_length=50, default=STATUS.active)
    stock_warning_threshold = models.PositiveIntegerField(default=5)

    @property
    def product_id(self):
        return self.id

    @property
    def qty(self):
        return ProductKeys.objects.filter(is_used=False, product=self.id, is_deleted=False).count()
    
    @property
    def used_stock(self):
        return ProductKeys.objects.filter(product=self.id, is_used=True, is_deleted=False).count()

    @property
    def stock(self):
        return ProductKeys.objects.filter(product=self.id, is_used=False, is_deleted=False).exists()

    def __str__(self):
        return self.description


class ProductKeys(UserStampedModel, TimeStampedModel):
    serial_no_value = models.CharField(max_length=255, blank=True, null=True)
    pin = models.CharField(max_length=255)
    is_used = models.BooleanField(default=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="keys"
    )

    used_order = models.ForeignKey(
        "products.Order",
        on_delete=models.CASCADE,
        related_name="used_product_keys",
        related_query_name="used_product_key",
        blank=True,
        null=True,
    )
    used_at = models.DateTimeField(
        blank=True,
        null=True
    )

    is_deleted = models.BooleanField(default=False)

    @property
    def order_number(self):
        return self.used_order.id

    @property
    def serial_no(self):
        return self.serial_no_value if self.serial_no_value else f'SN-{self.id:06d}-{self.product.id:04d}'

    @property
    def fib_order_number(self):
        return self.used_order.transaction_id

    @property
    def product_keys_left(self):
        return ProductKeys.objects.filter(product=self.product).filter(is_used=False).count()

    class Meta:
        ordering = ['-used_at', '-created']

    def __str__(self):
        return self.pin
    

class Notification(UserStampedModel, TimeStampedModel):
    title = models.CharField(max_length=255, default="Product Notification")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="notification_product",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title


class Order(UserStampedModel, TimeStampedModel):
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="order_product",
        blank=True,
        null=True
    )
    quantity = models.PositiveIntegerField()
    transaction_id = models.CharField(max_length=255)

    @property
    def price(self):
        return self.product_id.price

    @property
    def total_price(self):
        return self.product_id.price * self.quantity

    @property
    def product_name(self):
        return self.product_id.name

    @property
    def product_description(self):
        return self.product_id.description

    @property
    def product_image(self):
        return self.product_id.image.url

    def __str__(self):
        return str(self.id)


class OrderLines(UserStampedModel, TimeStampedModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="Cards",
        related_query_name="Cards"

    )
    # trxId = models.CharField(max_length=255, blank=True, null=True)
    product_key = ChainedForeignKey(
        ProductKeys,
        chained_field=Product,
        chained_model_field="order.product",
        related_name="order_line_key",
        related_query_name="order_line_keys",
        show_all=False,
        auto_choose=True,
        sort=True,
    )

    @property
    def price(self):
        return self.product_key.product.price

    @property
    def name(self):
        return self.product_key.product.name

    @property
    def description(self):
        return self.product_key.product.description

    @property
    def serial_no(self):
        return self.product_key.serial_no

    @property
    def pin(self):
        return self.product_key.pin

    @property
    def trxId(self):
        return self.id

    def __str__(self):
        return str(self.id)
