
from rest_framework import serializers
from ..models import FAQ

class CreateFAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQ
        fields = ['id', 'faq_name',  'faq_question', 'faq_answer']


class FAQListSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQ
        fields = ['id', 'faq_name',  'faq_question', 'faq_answer']