
from rest_framework import serializers
from ..models import Product

class CreateProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'product_name',  'subheading', 'product_image',
                  'price', 'product_qty', 'isActive', 'description', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'product_name',  'subheading', 'product_image', 'isActive',
                  'price', 'product_qty', 'description', 'created_at', 'updated_at']


    def get_product_image(self, obj):
        request = self.context.get("request")

        if not obj.product_image:
            return None

        if request:
            return request.build_absolute_uri(obj.product_image.url)

        return obj.product_image.url