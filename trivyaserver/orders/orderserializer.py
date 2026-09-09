
from rest_framework import serializers
from ..models import Order, Product, OrderDet

class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'order_code', 'payment_status', 'user', 
                  'total_quantity', 'total_price', 'created_at', 'updated_at']

        read_only_fields = ['id', 'order_code',
            'created_at', 'updated_at'
        ]


class CreateOrderDetSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDet
        fields = ['id', 'order', 'product', 'quantity',
                   'price', 'created_at', 'updated_at']


class CustomerOrderDetailSerializer(serializers.ModelSerializer):

    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    def get_product_name(self, obj):
        return obj.product.product_name

    def get_product_image(self, obj):
        request = self.context.get("request")

        if obj.product.product_image:
            return request.build_absolute_uri(
                obj.product.product_image.url
            )

        return None

    class Meta:
        model = OrderDet
        fields = ["id", "product", "product_name",
            "product_image", "quantity", "price",
            "created_at", "updated_at"]

class CustomerOrderListSerializer(serializers.ModelSerializer):

    customer_name = serializers.SerializerMethodField()
    order_details = CustomerOrderDetailSerializer(many=True, read_only=True)

    def get_customer_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    class Meta:
        model = Order
        fields = ["id", "order_code", "payment_status",
            "customer_name", "total_quantity", "total_price",
            "order_details", "created_at", "updated_at"
        ]