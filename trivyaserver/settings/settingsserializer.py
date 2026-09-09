
from rest_framework import serializers
from ..models import PaymentProvider, PaymentGatewayConfig

class GetPaymentProvidersListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentProvider
        fields = ['id', 'name']



class GetPaymentConfigDataSerializer(
    serializers.ModelSerializer
):

    provider_name = serializers.CharField(
        source="provider.name",
        read_only=True
    )

    key_secret_configured = serializers.SerializerMethodField()

    class Meta:
        model = PaymentGatewayConfig

        fields = [
            "id", "provider",
            "provider_name", "key_id", "key_secret_configured",
            "is_active", "created_at", "updated_at", "key_secret"
        ]

    def get_key_secret_configured(self, obj):
        return bool(obj.key_secret)


class CreatePaymentConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentGatewayConfig

        fields = [
            "provider",
            "key_id",
            "key_secret",
            "is_active",
        ]

    def validate_provider(self, value):

        if not PaymentProvider.objects.filter(
            id=value.id
        ).exists():

            raise serializers.ValidationError(
                "Payment provider does not exist."
            )

        return value

    def validate(self, attrs):

        provider = attrs.get("provider")

        # Prevent duplicate configuration
        # for the same provider.

        if PaymentGatewayConfig.objects.filter(
            provider=provider
        ).exists():

            raise serializers.ValidationError(
                {
                    "provider":
                    "Payment configuration already exists for this provider."
                }
            )

        return attrs



class UpdatePaymentConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentGatewayConfig

        fields = [
            "provider",
            "key_id",
            "key_secret",
            "is_active",
        ]

        extra_kwargs = {
            "key_secret": {
                "required": False,
                "allow_blank": True,
            }
        }

    def update(self, instance, validated_data):

        # If frontend sends an empty secret,
        # keep the existing secret.

        key_secret = validated_data.get(
            "key_secret",
            None
        )

        if key_secret == "":
            validated_data.pop(
                "key_secret",
                None
            )

        return super().update(
            instance,
            validated_data
        )