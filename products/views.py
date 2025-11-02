from rest_framework import mixins, viewsets
from rest_framework import filters, permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi
from drf_yasg.utils import no_body, swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Order, ProductKeys, OrderLines, Notification
from .serializers import ProductSerializer, ProductAdminSerializer, ProductKeysSerializer, OrderSerializer, OrderLinesSerializer, NotificationSerializer
from django_filters import rest_framework as django_filters_rest_framework

from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from .models import Order
from django.utils.dateparse import parse_date
from rest_framework.exceptions import ValidationError as drf_exceptions
from rest_framework.permissions import IsAdminUser
from core.utils import StandardLimitOffsetPagination

from rest_framework.decorators import action

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ProductViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Product.objects.exclude(
        is_deleted=True).exclude(status="inactive")
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = CustomPagination

    permission_classes = [permissions.IsAuthenticated]


class ProductAdminViewSet(
    viewsets.ModelViewSet
):
    queryset = Product.objects.exclude(is_deleted=True)
    serializer_class = ProductAdminSerializer
    filter_backends = [filters.SearchFilter,
                       filters.OrderingFilter, DjangoFilterBackend]
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['status']
    search_fields = ['name', 'description']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response({"status": True, "message": "Product deleted"})


class ProductKeyViewSet(
    viewsets.ModelViewSet
):
    queryset = ProductKeys.objects.exclude(
        is_deleted=True)
    serializer_class = ProductKeysSerializer
    filter_backends = [filters.SearchFilter,
                       django_filters_rest_framework.DjangoFilterBackend]
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAdminUser]
    search_fields = ['serial_no', 'pin']
    filterset_fields = ['is_used', 'product']

    def destroy(self, request, *args, **kwargs): 
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response({"status": True, "message": "Product deleted"})


class OrderViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet
                   ):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create Order",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "product_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Id of a product",
                ),
                "transaction_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The id of the transaction",
                ),
                "quantity": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The requested quantity",
                ),

            },
        ),

        responses={200: "OrderStats"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class OrderAdminViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = [permissions.IsAdminUser]
    pagination_class = CustomPagination

    search_fields = ['transaction_id']

    @swagger_auto_schema(
        operation_description="Create Order",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "product_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Id of a product",
                ),
                "transaction_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The id of the transaction",
                ),
                "quantity": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="The requested quantity",
                ),

            },
        ),

        responses={200: "OrderStats"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create Order",
        request_body=no_body, manual_parameters=[
            openapi.Parameter(
                name='start_date',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='Start date in YYYY-MM-DD format',
            ),
            openapi.Parameter(
                name='end_date',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='End date in YYYY-MM-DD format',
            ),
        ],
        responses={200: "OrderStats"},
    )
    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def total_sold_per_product_per_day(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required"}, status=400)

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        orders = (
            Order.objects.filter(created__date__range=[start_date, end_date])
            .values("product_id", "product_id__name")  # Group by product
            .annotate(
                date=TruncDate("created"),
                total_sold=Sum("quantity"),
                # Calculate total price
                total_price=Sum(F("quantity") * F("product_id__price")),
            )
            .order_by("date")
        )

        return Response({
            "data": list(orders)
        })

    @swagger_auto_schema(
        operation_description="Get stats for orders within a date range",
        manual_parameters=[
            openapi.Parameter(
                "created_after",
                openapi.IN_QUERY,
                description="Start date for filtering orders (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "created_before",
                openapi.IN_QUERY,
                description="End date for filtering orders (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "username",
                openapi.IN_QUERY,
                description="End date for filtering orders (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: "OrderStats"},
    )
    @action(
        detail=False,
        methods=["get"],
        filter_backends=None,
        pagination_class=StandardLimitOffsetPagination,
        permission_classes=[permissions.AllowAny],
    )
    def revenu(self, request):
        queryset = OrderLines.objects.all()
        start_date = request.query_params.get("created_after")
        end_date = request.query_params.get("created_before")
        username = request.query_params.get("username")

        if start_date:
            try:
                start_date = parse_date(start_date)
                if not start_date:
                    raise ValueError
            except ValueError:
                raise drf_exceptions(
                    {"created_after": "Invalid date format. Use YYYY-MM-DD."}
                )
            queryset = queryset.filter(created__gte=start_date)

        if end_date:
            try:
                end_date = parse_date(end_date)
                if not end_date:
                    raise ValueError
            except ValueError:
                raise drf_exceptions(
                    {"created_before": "Invalid date format. Use YYYY-MM-DD."}
                )
            queryset = queryset.filter(created__lte=end_date)

        if username:
            queryset = queryset.filter(
                created_by__username__icontains=username)

        paginator = StandardLimitOffsetPagination()

        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = OrderLinesSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # In case pagination is not applied (e.g., no results or invalid params)
        serializer = OrderLinesSerializer(queryset, many=True)
        return Response({
            "data": serializer.data,
            "total": queryset.count(),
        })


class TransactionSet(viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create Order",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "transaction_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The id of the transaction",
                ),
            },
        ),

        responses={200: "OrderStats"},
    )
    def create(self, request, *args, **kwargs):
        transaction_id = request.data.get("transaction_id")

        order = Order.objects.filter(transaction_id=transaction_id)

        if not order.exists():
            return Response({
                "status": False,
                "message": "Transaction not found",
            })

        order = order.first()

        return Response(OrderSerializer(order).data)


class NotificationViewSet(
    viewsets.ModelViewSet
):
    queryset = Notification.objects.exclude(is_read=True)
    serializer_class = NotificationSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['title', 'message']

    def get_queryset(self):
        return Notification.objects.filter(
            is_read=False).order_by('-created')

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": True, "message": "Notification marked as read"})
