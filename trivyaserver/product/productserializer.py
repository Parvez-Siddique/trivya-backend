from rest_framework import serializers
from ..models import Product, ProductDetails


class CreateProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            "product_name",
            "subheading",
            "description",
            "product_image",
            "isActive",
        ]


class ProductVariationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductDetails
        fields = [
            "id",
            "size_variation",
            "price_variation",
            "variation_image_one",
            "variation_image_two",
            "variation_image_three",
            "variation_image_four",
        ]


class CreateProductVariationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductDetails
        fields = [
            "size_variation",
            "price_variation",
            "variation_image_one",
            "variation_image_two",
            "variation_image_three",
            "variation_image_four",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):

    product_variations = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "subheading",
            "description",
            "product_image",
            "isActive",
            "created_at",
            "updated_at",
            "product_variations",
        ]

    def get_product_image(self, obj):
        request = self.context.get("request")

        if obj.product_image:
            if request:
                return request.build_absolute_uri(
                    obj.product_image.url
                )

            return obj.product_image.url

        return None

    def get_product_variations(self, obj):
        variations = obj.product_details.all()

        return ProductVariationSerializer(
            variations,
            many=True,
            context=self.context
        ).data


class ProductListSerializer(serializers.ModelSerializer):

    product_image = serializers.SerializerMethodField()
    product_variations = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "subheading",
            "description",
            "product_image",
            "isActive",
            "product_variations",
            "created_at",
            "updated_at",
        ]

    def get_product_image(self, obj):
        request = self.context.get("request")

        if obj.product_image:
            if request:
                return request.build_absolute_uri(
                    obj.product_image.url
                )

            return obj.product_image.url

        return None

    def get_product_variations(self, obj):
        return ProductVariationSerializer(
            obj.product_details.all(),
            many=True,
            context=self.context
        ).data


class ProductUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            "product_name",
            "subheading",
            "description",
            "product_image",
            "isActive",
        ]


class CartProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetails
        fields = [
            "id",
            "size_variation",
            "price_variation",
        ]


class CartProductSerializer(serializers.ModelSerializer):
    variation = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "product_image",
            "variation",
        ]

    def get_variation(self, obj):
        variation_id = self.context.get("variation_id")

        if not variation_id:
            return None

        variation = obj.product_details.filter(
            id=variation_id
        ).first()

        if not variation:
            return None

        return CartProductVariationSerializer(
            variation
        ).data



class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variation_id = serializers.IntegerField()
    product_count = serializers.IntegerField()

    product_name = serializers.CharField()
    product_image = serializers.SerializerMethodField()

    size_variation = serializers.CharField()
    price_variation = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        allow_null=True
    )

    def get_product_image(self, obj):
        request = self.context.get("request")

        product = obj["product"]

        if product.product_image:
            if request:
                return request.build_absolute_uri(
                    product.product_image.url
                )

            return product.product_image.url

        return None