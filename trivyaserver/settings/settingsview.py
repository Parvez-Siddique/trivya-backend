from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import PaymentProvider, PaymentGatewayConfig
from .settingsserializer import GetPaymentProvidersListSerializer, GetPaymentConfigDataSerializer, CreatePaymentConfigSerializer, UpdatePaymentConfigSerializer

from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication

class GetPaymentProvidersList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paymentProviders = PaymentProvider.objects.all().order_by("id")
        serializer = GetPaymentProvidersListSerializer(paymentProviders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetPaymentConfigData(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        payment_provider_id = request.query_params.get("payment_provider_id")
        paymentProviderData = PaymentGatewayConfig.objects.filter(provider=payment_provider_id).first()
        serializer = GetPaymentConfigDataSerializer(paymentProviderData)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePaymentConfig(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CreatePaymentConfigSerializer(data=request.data)

        if serializer.is_valid():

            payment_config = serializer.save()

            return Response(
                {
                    "status": "SUCCESS",
                    "message": "Payment configuration created successfully.",
                    "id": payment_config.id,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "status": "ERROR",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )



class UpdatePaymentConfig(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):

        payment_gateway_id = request.query_params.get("payment_gateway_id")

        if not payment_gateway_id:

            return Response(
                {
                    "status": "ERROR",
                    "error": "payment_gateway_id is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            payment_gateway_config = (
                PaymentGatewayConfig.objects.get(
                    pk=payment_gateway_id
                )
            )

        except PaymentGatewayConfig.DoesNotExist:

            return Response(
                {
                    "status": "ERROR",
                    "error": "Payment Gateway configuration not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )


        serializer = UpdatePaymentConfigSerializer(payment_gateway_config, data=request.data,partial=True)

        if serializer.is_valid():

            payment_gateway_config = serializer.save()

            return Response(
                {
                    "status": "SUCCESS",
                    "message": "Payment configuration updated successfully.",
                    "id": payment_gateway_config.id,
                },
                status=status.HTTP_200_OK
            )


        return Response(
            {
                "status": "ERROR",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )