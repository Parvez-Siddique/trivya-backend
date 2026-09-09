from .models import PaymentProvider


DEFAULT_PAYMENT_PROVIDERS = [
    {
        "name": "Razorpay",
        "code": "RAZORPAY",
    },
    {
        "name": "Stripe",
        "code": "STRIPE",
    },
    {
        "name": "PayPal",
        "code": "PAYPAL",
    },
]


def create_default_payment_providers():
    """
    Creates default payment providers if they don't already exist.
    """

    for provider in DEFAULT_PAYMENT_PROVIDERS:

        PaymentProvider.objects.get_or_create(
            code=provider["code"],
            defaults={
                "name": provider["name"],
                "is_active": True,
            },
        )