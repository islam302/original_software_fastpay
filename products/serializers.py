from rest_framework import serializers
from .models import Product, ProductKeys, Order, OrderLines, Notification
from authentication.models import User
from django.db import transaction
from rest_framework import filters
from django.utils import timezone

from core.serializer_fields import (
    Base64ImageField
)


class ProductSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)

    class Meta:
        model = Product
        fields = (
            "product_id", "name", "description", "price", "image", "stock"
        )


class ProductKeysSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductKeys
        fields = (
            "id", "serial_no", "pin", "is_used", "is_deleted", "product", "used_order", "order_number", "fib_order_number", "product_keys_left", "created", "created_by", "modified", "updated_by"
        )
        read_only_fields = (
            "created_by",
            "updated_by"
        )


class ProductAdminSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    keys = ProductKeysSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "product_id", "name", "description", "price", "image", "stock", "qty","stock_warning_threshold", "status", "created", "created_by", "modified", "updated_by", "keys"
        )

    def to_representation(self, instance):
        """Filter out keys where is_deleted=True"""
        representation = super().to_representation(instance)
        representation["keys"] = [
            key for key in representation["keys"] if not key.get("is_deleted", False)
        ]
        return representation


class NotificationSerializer(serializers.ModelSerializer):
    product_data = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id", "title", "message", "is_read", "product", "product_data", "created",  "modified"
        )
        read_only_fields = (
            "created",
            "modified"
        )


class OrderLinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLines
        fields = (
            "id", "trxId", "serial_no", "pin", "name", "description", "price", "order", "created", "created_by", "modified", "updated_by"
        )
        read_only_fields = (
            "created_by",
            "updated_by"
            "created",
            "modified"
        )


class OrderSerializer(serializers.ModelSerializer):
    # Assuming multiple lines per order
    Cards = OrderLinesSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "transaction_id", "product_id",
                  "quantity", "Cards", "product_name", "price", "total_price", "product_description", "product_image", "created", "created_by", "modified", "updated_by")

        read_only_fields = (
            "created_by",
            "updated_by"
            "created",
            "modified"
        )

    def validate(self, attrs):
        """Custom validation before creating an order."""
        product_id = attrs.get(
            "product_id").id  # Assuming product is a ForeignKey
        qty = attrs.get("quantity")
        transaction_id = attrs.get("transaction_id")

        if not Product.objects.filter(id=product_id).exists():
            raise serializers.ValidationError({
                "message": "Product not found",
                "transaction_id": f"{transaction_id}"
            })

        available_keys = ProductKeys.objects.filter(
            product=product_id, is_used=False, is_deleted=False).count()

        if qty > available_keys:
            raise serializers.ValidationError({
                "message": "Not enough keys available",
                "transaction_id": f"{transaction_id}"
            })

        return attrs  # Must return attrs after validation

    def create(self, validated_data):
        with transaction.atomic():
            qty = validated_data.pop("quantity")
            product_id = validated_data.pop("product_id")
            transaction_id = validated_data.get("transaction_id")

            order = Order.objects.create(
                **validated_data, product_id=product_id, quantity=qty)

            remaining_qty = qty
            for key in ProductKeys.objects.filter(product=product_id, is_used=False, is_deleted=False)[:qty]:
                OrderLines.objects.create(order=order, product_key=key)
                key.is_used = True
                key.used_at = timezone.now()
                key.used_order = order
                key.save()
                remaining_qty -= 1

            if ProductKeys.objects.filter(product=product_id, is_used=False, is_deleted=False).count() <= Product.objects.get(id=product_id.id).stock_warning_threshold:
                product = Product.objects.get(id=product_id.id)
                Notification.objects.create(
                    title="Low Stock Warning",
                    message=f"The stock for product '{product.name}' is low. Only {ProductKeys.objects.filter(product=product_id, is_used=False, is_deleted=False).count()} keys left.",
                    product=product
                )

            order.save()
            return order
