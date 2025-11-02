from django.contrib import admin

import nested_admin

from django.db.models import JSONField

from .models import Product, ProductKeys, Order, OrderLines


class ProductKeysInline(admin.TabularInline):
    model = ProductKeys
    fk_name = "product"
    extra = 0
    ordering = ("id",)
    readonly_fields = ("is_used",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "serial_no_value",
                    "pin",
                    "is_used",
                    "is_deleted",
                    "product",
                )
            },
        ),
    )


class OrderLinesInline(admin.TabularInline):
    model = OrderLines
    fk_name = "order"
    extra = 0
    ordering = ("id",)
    readonly_fields = (
        "serial_no",
        "pin",
        "product_key",
        "trxId",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "serial_no",
                    "pin",
                    "product_key",
                    "trxId",
                )
            },
        ),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = (
        "stock",
        "qty",
        "created",
        "modified",
        "created_by",
        "updated_by",
    )
    list_display = (
        "id",
        "name",
        "stock",
        "qty",
        "created",
        # "qty_modified_from_zero",
    )
    list_display_links = ("id", "name")
    list_filter = (
        "is_deleted",
    )
    search_fields = (
        "name",
    )
    ordering = ("name",)
    fieldsets = (
        (
            "Product Info",
            {
                "fields": (
                    "name",
                    "description",
                    "price",
                    "image",
                    "stock",
                    "is_deleted"
                )
            },
        ),
        (
            "Technical Info",
            {
                "fields": (
                    "created",
                    "modified",
                    "created_by",
                    "updated_by",
                )
            },
        ),
    )

    inlines = [ProductKeysInline]


@admin.register(Order)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = (
        "product_id",
        "quantity",
        "created",
        "modified",
        "created_by",
        "updated_by",
    )
    list_display = (
        "id",
        "product_name",
        "quantity",
        "created",
        # "qty_modified_from_zero",
    )
    list_display_links = ("id", "product_name")
    list_filter = (
        "product_id",
    )
    search_fields = (
        "id",
        "product_name"
    )
    ordering = ("id",)
    fieldsets = (
        (
            "Order Info",
            {
                "fields": (
                    "product_id",
                    "quantity",
                )
            },
        ),
        (
            "Technical Info",
            {
                "fields": (
                    "created",
                    "modified",
                    "created_by",
                    "updated_by",
                )
            },
        ),
    )

    inlines = [OrderLinesInline]
