from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import FAQ
from .faqserializer import CreateFAQSerializer, FAQListSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny
from knox.auth import TokenAuthentication

class FAQCreateView(APIView):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateFAQSerializer(data=request.data)
    
        if serializer.is_valid():
            serializer.save()

            return Response(
                {"status": "SUCCESS"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def get(self, request):
        products = FAQ.objects.all().order_by("id")
        serializer = FAQListSerializer(products, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        faq_id = request.query_params.get("faq_id")

        if not faq_id:
            return Response(
                {
                    "status": "ERROR",
                    "error": "FAQ ID is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            faq = FAQ.objects.get(pk=faq_id)

        except faq.DoesNotExist:
            return Response(
                {
                    "status": "ERROR",
                    "error": "FAQ not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        faq.delete()

        return Response(
            {
                "status": "SUCCESS",
                "message": "Product deleted successfully"
            },
            status=status.HTTP_200_OK
        )

class FAQUpdateView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            faqId = request.query_params.get("faq_id")
            faq = FAQ.objects.get(pk=faqId)
        except faq.DoesNotExist:
            return Response(
                {"error": "FAQ not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FAQListSerializer(
            faq,
            context={"request": request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request):
        try:
            faqId = request.query_params.get("faq_id")
            faq = FAQ.objects.get(pk=faqId)

        except faq.DoesNotExist:
            return Response(
                {
                    "status": "ERROR",
                    "error": "FAQ not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CreateFAQSerializer(
            faq,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            faq = serializer.save()

            return Response(
                {
                    "status": "SUCCESS"
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


class FAQStatusChangeView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        faq_id = request.data.get("faqId")
        is_active = request.data.get("isActive")

        if not faq_id:
            return Response(
                {
                    "status": "ERROR",
                    "error": "FAQ ID is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if is_active is None:
            return Response(
                {
                    "status": "ERROR",
                    "error": "isActive is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            faq = FAQ.objects.get(pk=faq_id)

        except faq.DoesNotExist:
            return Response(
                {
                    "status": "ERROR",
                    "error": "FAQ not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Update product status
        faq.isActive = is_active
        faq.save()

        return Response(
            {
                "status": "SUCCESS",
                "message": "Product status updated successfully",
                "isActive": faq.isActive
            },
            status=status.HTTP_200_OK
        )


class FAQPublicListView(APIView):
    
    permission_classes = [AllowAny]

    def get(self, request):
        products = FAQ.objects.all().order_by("id")
        serializer = FAQListSerializer(products, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)