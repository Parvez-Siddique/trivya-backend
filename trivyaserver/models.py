from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.



class UserManager(BaseUserManager):

    def create_user(
        self, email,
        password=None, **extra_fields
    ):

        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email,
        password=None,
        **extra_fields
    ):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )

        return self.create_user(
            email=email,
            password=password,
            **extra_fields
        )

class User(AbstractUser):

    class UserType(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        CUSTOMER = "CUSTOMER", "Customer"

    username = models.CharField(max_length=150, blank=True, null=True)

    firstName = models.CharField(max_length=150, null=True)

    lastName = models.CharField(max_length=150, null=True)

    email = models.EmailField(unique=True)

    phoneNumber = models.CharField(max_length=15, unique=True, blank=True, null=True)

    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.ADMIN)

    streetName = models.CharField( max_length=255, blank=True, null=True )

    area = models.CharField( max_length=150, blank=True, null=True )

    city = models.CharField( max_length=150, blank=True, null=True )

    state = models.CharField( max_length=150, blank=True, null=True )

    pincode = models.CharField( max_length=10, blank=True, null=True )

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email


class UserDetails(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user_details")
    field_name = models.CharField(max_length=150, null=True)
    field_data = models.CharField(max_length=150, null=True)


class Product(models.Model):
    product_name = models.CharField(max_length=200)
    subheading = models.CharField(max_length=300)
    description = models.TextField()

    product_image = models.ImageField(upload_to='products/')

    
    isActive = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name


class ProductDetails(models.Model):
    
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="product_details")
    size_variation = models.CharField(max_length=200)
    price_variation = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    variation_image_one = models.ImageField(upload_to='productvariations/',null=True, blank=True)
    variation_image_two = models.ImageField(upload_to='productvariations/', null=True, blank=True)
    variation_image_three = models.ImageField(upload_to='productvariations/', null=True, blank=True)
    variation_image_four = models.ImageField(upload_to='productvariations/', null=True, blank=True)

    def __str__(self):
        return self.size_variation

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

    order_status = models.CharField(max_length=20, default="PENDING")

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

    product_size = models.CharField(max_length=100, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order Detail #{self.id}"