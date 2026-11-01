from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Order, User, UserDetails, PaymentGatewayConfig
from .orderserializer import CreateOrderSerializer, CustomerOrderListSerializer, CreateOrderDetSerializer, CreateCustomerSerializer, UpdateOrderStatusSerializer
from django.db import transaction
from django.db.models import Q
from rest_framework.permissions import AllowAny
import razorpay
from django.shortcuts import get_object_or_404
from decimal import Decimal, ROUND_HALF_UP

def get_razorpay_client():

    config = PaymentGatewayConfig.objects.select_related(
        "provider"
    ).get(
        provider__name__iexact="Razorpay",
        is_active=True
    )

    client = razorpay.Client(
        auth=(
            config.key_id,
            config.key_secret
        )
    )

    return client, config.key_id

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


class PlaceOrderView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        customer_data = request.data.get("customer_data")
        order_data = request.data.get("order_data")

        if not customer_data:
            return Response(
                {"status": "FAILED"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not order_data:
            return Response(
                {"status": "FAILED"},
                status=status.HTTP_400_BAD_REQUEST
            )

        customer_email = customer_data.get("email")
        customer_phone = customer_data.get("phoneNumber")

        fetch_user_data = User.objects.filter(
            user_type="CUSTOMER"
        ).filter(
            Q(email=customer_email) |
            Q(phoneNumber=customer_phone)
        ).first()

        if fetch_user_data:

            user_id = fetch_user_data.id

            if (
                customer_phone
                and fetch_user_data.phoneNumber != customer_phone
            ):

                phone_exists = User.objects.filter(
                    user_type="CUSTOMER",
                    phoneNumber=customer_phone
                ).exclude(
                    id=user_id
                ).exists()

                if phone_exists:
                    return Response(
                        {"status": "FAILED"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                fetch_user_data.phoneNumber = customer_phone

            if (
                customer_email
                and fetch_user_data.email != customer_email
            ):

                email_exists = User.objects.filter(
                    user_type="CUSTOMER",
                    email=customer_email
                ).exclude(
                    id=user_id
                ).exists()

                if email_exists:
                    return Response(
                        {"status": "FAILED"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                fetch_user_data.email = customer_email


            fetch_user_data.save()

        else:

            customer_serializer = CreateCustomerSerializer(
                data=customer_data
            )

            if not customer_serializer.is_valid():

                return Response(
                    {"status": "FAILED"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_user = customer_serializer.save()

            user_id = new_user.id

        order_data["user"] = user_id

        order_details_data = order_data.get(
            "order_details",
            []
        )


        order_serializer = CreateOrderSerializer(data=order_data)

        if not order_serializer.is_valid():

            return Response(
                {"status": "FAILED"},
                status=status.HTTP_400_BAD_REQUEST
            )


        try:

            with transaction.atomic():

                order_code, order_code_count = (
                    generate_order_code()
                )

                order = order_serializer.save(
                    order_code=order_code,
                    order_code_count=order_code_count
                )

                # ------------------------------------------
                # Create order details
                # ------------------------------------------

                for order_detail in order_details_data:

                    order_detail["order"] = order.id

                    order_detail_serializer = (
                        CreateOrderDetSerializer(
                            data=order_detail
                        )
                    )

                    if not order_detail_serializer.is_valid():

                        return Response(
                            {"status": "FAILED"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    order_detail_serializer.save()

            return Response(
                {"status": "SUCCESS", "order_id": order.id, "order_code": order.order_code},
                status=status.HTTP_201_CREATED
            )

        except Exception as error:

            return Response(
                {"status": "FAILED"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateOrderStatus(APIView):

    permission_classes = [AllowAny]

    def put(self, request):

        serializer = UpdateOrderStatusSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                {
                    "success": False,
                    "error": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order_id = serializer.validated_data.get("order_id")
        payment_status = serializer.validated_data.get("payment_status")
        order_status = serializer.validated_data.get("order_status")

        try:

            order = Order.objects.get(
                id=order_id
            )

        except Order.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "error": "Order not found",
                },
                status=status.HTTP_404_NOT_FOUND
            )

        order.payment_status = payment_status
        order.order_status = order_status

        order.save(
            update_fields=[
                "payment_status",
                "order_status",
                "updated_at",
            ]
        )

        return Response(
            {
                "success": True,
                "message": "Order status updated successfully",
                "data": {
                    "order_id": order.id,
                    "order_code": order.order_code,
                    "payment_status": order.payment_status,
                    "order_status": order.order_status,
                },
            },
            status=status.HTTP_200_OK
        )


class CreatePaymentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        order_id = request.data.get("order_id")

        print(f"Received order_id: {order_id}")

        if not order_id:
            return Response(
                {"error": "Order ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = get_object_or_404(
            Order,
            id=order_id
        )

        print(f"Order found: {order}")

        if order.payment_status == "SUCCESS":
            return Response(
                {"error": "Order already paid"},
                status=status.HTTP_400_BAD_REQUEST
            )

        amount = int(
            (order.total_price * Decimal("100")).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP
            )
        )

        print(f"Calculated amount in paise: {amount}")

        if amount <= 0:
            return Response(
                {"error": "Invalid payment amount"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            razorpay_client, key_id = get_razorpay_client()

            if not order.razorpay_order_id:

                razorpay_order = razorpay_client.order.create({
                    "amount": amount,
                    "currency": "INR",
                    "receipt": order.order_code
                })

                order.razorpay_order_id = razorpay_order["id"]

                order.save(update_fields=[
                    "razorpay_order_id",
                    "updated_at"
                ])

            return Response({
                "status": "SUCCESS",
                "key": key_id,
                "razorpay_order_id": order.razorpay_order_id,
                "amount": amount,
                "currency": "INR",
                "order_code": order.order_code
            }, status=status.HTTP_200_OK)

        except PaymentGatewayConfig.DoesNotExist:

            return Response(
                {"error": "Razorpay configuration not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        except PaymentGatewayConfig.MultipleObjectsReturned:

            return Response(
                {"error": "Multiple active Razorpay configurations found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception:

            return Response(
                {"error": "Unable to initiate payment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class VerifyPaymentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        order_id = request.data.get("order_id")
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        # 1. Validate required fields
        if not all([
            order_id,
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        ]):
            return Response(
                {
                    "status": "FAILED",
                    "error": "All payment details are required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            razorpay_client, key_id = get_razorpay_client()

            # 2. Lock the application order
            with transaction.atomic():

                order = Order.objects.select_for_update().get(
                    id=order_id
                )

                # 3. Prevent verification against another Razorpay order
                if order.razorpay_order_id != razorpay_order_id:
                    return Response(
                        {
                            "status": "FAILED",
                            "error": "Razorpay order ID mismatch"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # 4. Handle duplicate verification requests
                if order.payment_status == "SUCCESS":
                    if order.razorpay_payment_id == razorpay_payment_id:
                        return Response({
                            "status": "SUCCESS",
                            "message": "Payment already verified",
                            "order_code": order.order_code
                        })

                    return Response(
                        {
                            "status": "FAILED",
                            "error": "This order has already been paid"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # 5. Verify Razorpay signature
                try:
                    razorpay_client.utility.verify_payment_signature({
                        "razorpay_order_id": order.razorpay_order_id,
                        "razorpay_payment_id": razorpay_payment_id,
                        "razorpay_signature": razorpay_signature
                    })

                except razorpay.errors.SignatureVerificationError:
                    return Response(
                        {
                            "status": "FAILED",
                            "error": "Invalid payment signature"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # 6. Fetch actual payment details from Razorpay
                payment = razorpay_client.payment.fetch(
                    razorpay_payment_id
                )

                # 7. Calculate expected amount in paise
                expected_amount = int(
                    (order.total_price * Decimal("100")).quantize(
                        Decimal("1"),
                        rounding=ROUND_HALF_UP
                    )
                )

                # 8. Verify payment details
                if payment.get("order_id") != order.razorpay_order_id:
                    return Response(
                        {
                            "status": "FAILED",
                            "error": "Payment does not belong to this order"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if payment.get("amount") != expected_amount:
                    return Response(
                        {
                            "status": "FAILED",
                            "error": "Payment amount mismatch"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if payment.get("currency") != "INR":
                    return Response(
                        {
                            "status": "FAILED",
                            "error": "Payment currency mismatch"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # 9. Confirm payment is captured
                if payment.get("status") != "captured":
                    return Response(
                        {
                            "status": "FAILED",
                            "error": "Payment is not captured yet",
                            "payment_status": payment.get("status")
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # 10. Update application order
                order.payment_status = "SUCCESS"
                order.razorpay_payment_id = razorpay_payment_id
                order.payment_signature = razorpay_signature

                order.save(update_fields=[
                    "payment_status",
                    "razorpay_payment_id",
                    "payment_signature",
                    "updated_at"
                ])

                return Response({
                    "status": "SUCCESS",
                    "message": "Payment verified successfully",
                    "order_id": order.id,
                    "order_code": order.order_code
                }, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response(
                {
                    "status": "FAILED",
                    "error": "Order not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except PaymentGatewayConfig.DoesNotExist:
            return Response(
                {
                    "status": "FAILED",
                    "error": "Razorpay configuration not found"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as error:
            print("Payment verification error:", str(error))

            return Response(
                {
                    "status": "FAILED",
                    "error": "Unable to verify payment"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )