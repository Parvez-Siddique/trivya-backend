
from rest_framework import serializers
from ..models import Order, OrderDet, User

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
                   'price', 'product_size', 'created_at', 'updated_at']


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
            "product_image", "quantity", "price", "product_size",
            "created_at", "updated_at"]

class CustomerOrderListSerializer(serializers.ModelSerializer):

    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    customer_street = serializers.SerializerMethodField()
    customer_area = serializers.SerializerMethodField()
    customer_city = serializers.SerializerMethodField()
    customer_state = serializers.SerializerMethodField()
    customer_pincode = serializers.SerializerMethodField()
    order_details = CustomerOrderDetailSerializer(many=True, read_only=True)

    def get_customer_name(self, obj):
        return f"{obj.user.firstName} {obj.user.lastName}".strip()

    def get_customer_phone(self, obj):
                return f"{obj.user.phoneNumber}".strip()

    def get_customer_email(self, obj):
                    return f"{obj.user.email}".strip()

    def get_customer_street(self, obj):
                return f"{obj.user.streetName}".strip()

    def get_customer_area(self, obj):
                return f"{obj.user.area}".strip()

    def get_customer_city(self, obj):
                return f"{obj.user.city}".strip()

    def get_customer_state(self, obj):
                return f"{obj.user.state}".strip()

    def get_customer_pincode(self, obj):
            return f"{obj.user.pincode}".strip()


    class Meta:
        model = Order
        fields = ["id", "order_code", "payment_status", "order_status",
            "customer_name", "customer_phone","customer_email",
              "total_quantity", "customer_street", "customer_area",
              "customer_city", "customer_state", "customer_pincode",
              "total_price", "order_details", "created_at", "updated_at"
        ]


class CreateCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [ "firstName", "lastName", "email", "phoneNumber", 
                  "user_type", "streetName", "area", "city", "state", "pincode"]

    def create(self, validated_data): 
        user = User( **validated_data ) 
        user.save() 
        return user


class UpdateOrderStatusSerializer(serializers.Serializer):

    order_id = serializers.IntegerField()

    payment_status = serializers.CharField(
        max_length=20
    )

    order_status = serializers.CharField(
        max_length=20
    )