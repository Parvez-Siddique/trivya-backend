from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Product
from .productserializer import CreateProductSerializer, ProductListSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny
from knox.auth import TokenAuthentication

class ProductCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print("Request Data:", request.data)  # Debugging line to print the incoming request data
        serializer = CreateProductSerializer(data=request.data)
    
        if serializer.is_valid():

            print("JIJIGJIGJIGJ")
            product = serializer.save()

            return Response(
                {"status": "SUCCESS"},
                status=status.HTTP_201_CREATED
            )
        print("Serializer Errors:", serializer.errors)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def get(self, request):
        products = Product.objects.all().order_by("id")
        serializer = ProductListSerializer(products, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        product_id = request.query_params.get("product_id")

        if not product_id:
            return Response(
                {
                    "status": "ERROR",
                    "error": "Product ID is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(pk=product_id)

        except Product.DoesNotExist:
            return Response(
                {
                    "status": "ERROR",
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        product.delete()

        return Response(
            {
                "status": "SUCCESS",
                "message": "Product deleted successfully"
            },
            status=status.HTTP_200_OK
        )

class ProductUpdateView(APIView):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            productId = request.query_params.get("product_id")
            product = Product.objects.get(pk=productId)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductListSerializer(
            product,
            context={"request": request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request):
        try:
            productId = request.query_params.get("product_id")
            product = Product.objects.get(pk=productId)

        except Product.DoesNotExist:
            return Response(
                {
                    "status": "ERROR",
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CreateProductSerializer(
            product,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            product = serializer.save()

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


class ProductStatusChangeView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        product_id = request.data.get("productId")
        is_active = request.data.get("isActive")

        if not product_id:
            return Response(
                {
                    "status": "ERROR",
                    "error": "Product ID is required"
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
            product = Product.objects.get(pk=product_id)

        except Product.DoesNotExist:
            return Response(
                {
                    "status": "ERROR",
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Update product status
        product.isActive = is_active
        product.save()

        return Response(
            {
                "status": "SUCCESS",
                "message": "Product status updated successfully",
                "isActive": product.isActive
            },
            status=status.HTTP_200_OK
        )


class ProductPublicListViewAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.filter(isActive=True).order_by("id")
        serializer = ProductListSerializer(products, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)