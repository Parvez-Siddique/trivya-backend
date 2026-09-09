from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Order
from .orderserializer import CreateOrderSerializer, CustomerOrderListSerializer, CreateOrderDetSerializer
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, AllowAny
from knox.auth import TokenAuthentication

def generate_order_code():
    last_order = Order.objects.order_by("-order_code_count").first()

    if not last_order:
        count = 1
    else:
        count = last_order.order_code_count + 1

    return f"ORD{count:06d}", count
    

class OrderCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = CreateOrderSerializer(data=request.data)
        orderDetData = request.data.get("order_details", [])

        with transaction.atomic():
            if serializer.is_valid():
                order_code, order_code_count = generate_order_code()

                order = serializer.save(
                    order_code=order_code,
                    order_code_count=order_code_count
                )

                for orderDet in orderDetData:
                    orderDet['order'] = order.id
                    orderDetSerializer = CreateOrderDetSerializer(data=orderDet)
                    if orderDetSerializer.is_valid():
                        orderDetSerializer.save()
                    else:
                        return Response(
                            orderDetSerializer.errors,
                            status=status.HTTP_400_BAD_REQUEST
                        )

            return Response(
                {"status": "SUCCESS"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def get(self, request):
        orders = Order.objects.all().order_by("id")
        serializer = CustomerOrderListSerializer(orders, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyOrdersListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        customer_id = request.query_params.get("customer_id")
        if not customer_id:
            return Response(
                {"error": "customer_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        orders = Order.objects.filter(user_id=customer_id).order_by("id")
        serializer = CustomerOrderListSerializer(orders, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)