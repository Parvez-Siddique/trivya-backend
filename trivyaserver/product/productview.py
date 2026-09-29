from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Product, ProductDetails
from django.db import transaction

from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from .productserializer import (
    CreateProductSerializer, ProductListSerializer,
    ProductDetailSerializer,
    ProductUpdateSerializer,
    ProductVariationSerializer,
    CreateProductVariationSerializer,
    CartItemSerializer
)
import json

class ProductCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        product_data = request.data.get("product_data")

        product_variation_data = request.data.get(
            "product_variation_data",
            []
        )

        if isinstance(product_data, str):
            product_data = json.loads(product_data)

        if isinstance(product_variation_data, str):
            product_variation_data = json.loads(product_variation_data)

        product_image = request.FILES.get("product_image")

        if product_image:
            product_data["product_image"] = product_image

        serializer = CreateProductSerializer(data=product_data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        product = serializer.save()

        for index, variation in enumerate(product_variation_data):

            variation_number = index + 1

            variation_image_one = request.FILES.get(
                f"variation_{variation_number}_variation_image_one"
            )

            variation_image_two = request.FILES.get(
                f"variation_{variation_number}_variation_image_two"
            )

            variation_image_three = request.FILES.get(
                f"variation_{variation_number}_variation_image_three"
            )

            variation_image_four = request.FILES.get(
                f"variation_{variation_number}_variation_image_four"
            )

            ProductDetails.objects.create(
                product=product,
                size_variation=variation.get("size_variation"),
                price_variation=variation.get("price_variation"),

                variation_image_one=variation_image_one,
                variation_image_two=variation_image_two,
                variation_image_three=variation_image_three,
                variation_image_four=variation_image_four,
            )

        return Response(
            {
                "status": "SUCCESS",
                "product_id": product.id,
            },
            status=status.HTTP_201_CREATED
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


class ProductUpdateView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

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
            product = Product.objects.prefetch_related(
                "product_details"
            ).get(pk=product_id)

        except Product.DoesNotExist:
            return Response(
                {
                    "status": "ERROR",
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductDetailSerializer(
            product,
            context={"request": request}
        )

        return Response(
            {
                "status": "SUCCESS",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request):

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

        product_data = request.data.get("product_data")

        product_variation_data = request.data.get(
            "product_variation_data",
            []
        )

        if isinstance(product_data, str):
            product_data = json.loads(product_data)

        if isinstance(product_variation_data, str):
            product_variation_data = json.loads(product_variation_data)


        product_image = request.FILES.get("product_image")

        if product_data is not None:

            if product_image:
                product_data["product_image"] = product_image

            product_serializer = ProductUpdateSerializer(
                product,
                data=product_data,
                partial=True
            )

            if not product_serializer.is_valid():
                return Response(
                    {
                        "status": "ERROR",
                        "errors": {
                            "product": product_serializer.errors
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            product = product_serializer.save()

        existing_variations = ProductDetails.objects.filter(product=product)

        for variation in existing_variations:

            # Delete variation image files
            if variation.variation_image_one:
                variation.variation_image_one.delete(save=False)

            if variation.variation_image_two:
                variation.variation_image_two.delete(save=False)

            if variation.variation_image_three:
                variation.variation_image_three.delete(save=False)

            if variation.variation_image_four:
                variation.variation_image_four.delete(save=False)

            # Delete variation record
            variation.delete()

        # =================================
        # CREATE NEW VARIATIONS
        # =================================

        for index, variation in enumerate(product_variation_data):

            variation_number = index + 1

            # --------------------------------
            # Get variation images
            # --------------------------------

            variation_image_one = request.FILES.get(
                f"variation_{variation_number}_variation_image_one"
            )

            variation_image_two = request.FILES.get(
                f"variation_{variation_number}_variation_image_two"
            )

            variation_image_three = request.FILES.get(
                f"variation_{variation_number}_variation_image_three"
            )

            variation_image_four = request.FILES.get(
                f"variation_{variation_number}_variation_image_four"
            )

            # --------------------------------
            # Create variation
            # --------------------------------

            variation_serializer = CreateProductVariationSerializer(
                data=variation
            )

            if not variation_serializer.is_valid():
                return Response(
                    {
                        "status": "ERROR",
                        "errors": {
                            "variation": variation_serializer.errors
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_variation = variation_serializer.save(
                product=product
            )

            # --------------------------------
            # Save images
            # --------------------------------

            if variation_image_one:
                new_variation.variation_image_one = variation_image_one

            if variation_image_two:
                new_variation.variation_image_two = variation_image_two

            if variation_image_three:
                new_variation.variation_image_three = variation_image_three

            if variation_image_four:
                new_variation.variation_image_four = variation_image_four

            new_variation.save()

        product.refresh_from_db()

        serializer = ProductDetailSerializer(
            product, context={"request": request}
        )

        return Response(
            {
                "status": "SUCCESS",
                "message": "Product updated successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


    @transaction.atomic
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
        ProductDetails.objects.filter(
            product=product
        ).delete()

        product.delete()

        return Response(
            {
                "status": "SUCCESS",
                "message": "Product deleted successfully"
            },
            status=status.HTTP_200_OK
        )



class GetPublicProductDetails(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

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
            product = Product.objects.prefetch_related(
                "product_details"
            ).get(pk=product_id)

        except Product.DoesNotExist:
            return Response(
                {
                    "status": "ERROR",
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductDetailSerializer(
            product,
            context={"request": request}
        )

        return Response(
            {
                "status": "SUCCESS",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class GetCartDetails(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        cart = request.data.get("cart", [])

        if not isinstance(cart, list):
            return Response(
                {
                    "status": "FAILED",
                    "message": "Cart must be a list."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        response_data = []

        for cart_item in cart:

            product_id = cart_item.get("product_id")
            variation_id = cart_item.get("variation_id")
            product_count = cart_item.get("product_count", 1)

            if not product_id or not variation_id:
                continue

            product = Product.objects.filter(
                id=product_id,
                isActive=True
            ).first()

            if not product:
                continue

            variation = ProductDetails.objects.filter(
                id=variation_id,
                product=product
            ).first()

            if not variation:
                continue

            response_data.append(
                {
                    "product_id": product.id,
                    "variation_id": variation.id,
                    "product_count": product_count,

                    "product_name": product.product_name,

                    "product": product,

                    "size_variation": variation.size_variation,
                    "price_variation": variation.price_variation,
                }
            )

        serializer = CartItemSerializer(
            response_data,
            many=True,
            context={
                "request": request
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )