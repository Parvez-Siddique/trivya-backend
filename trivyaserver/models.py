from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):

    class UserType(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        CUSTOMER = "CUSTOMER", "Customer"


    firstName = models.CharField(max_length=150, null=True)

    lastName = models.CharField(max_length=150, null=True)

    email = models.EmailField(unique=True)

    phoneNumber = models.CharField(max_length=15, unique=True, blank=True, null=True)

    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.CUSTOMER)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username



class Product(models.Model):
    product_name = models.CharField(max_length=200)
    subheading = models.CharField(max_length=300)
    description = models.TextField()

    product_image = models.ImageField(
        upload_to='products/'
    )

    price = models.DecimalField(max_digits=10,decimal_places=2)
    product_qty = models.CharField(max_length=200)

    isActive = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name



class FAQ(models.Model):
    faq_name = models.CharField(max_length=200)
    faq_question = models.TextField()
    faq_answer = models.TextField()
    
    def __str__(self):
        return self.faq_name


class PaymentProvider(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=50,
        unique=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class PaymentGatewayConfig(models.Model):

    provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.PROTECT,
        related_name="gateway_configs"
    )

    key_id = models.CharField(max_length=255)

    key_secret = models.CharField(max_length=500)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider.name} Configuration"



class Order(models.Model):
    order_code = models.CharField(max_length=20, unique=True)

    order_code_count = models.PositiveIntegerField(default=0)

    payment_status = models.CharField(max_length=20, default="PENDING")

    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="orders")

    total_quantity = models.PositiveIntegerField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderDet(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_details")

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_details")

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order Detail #{self.id}"