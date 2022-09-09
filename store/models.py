from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from authentication.models import Person, Address


class Image(models.Model):
    image = models.ImageField(max_length=1000, unique=True, null=False, upload_to="static/images/product-images/")
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        ordering = ["id"]


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        ordering = ["name"]


class Category(models.Model):
    title = models.CharField(max_length=255, unique=True, null=False)
    slug = models.SlugField(max_length=300, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Categories"


class Product(models.Model):
    title = models.CharField(max_length=255, unique=True, null=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    info = models.TextField(max_length=1000, blank=True, null=True)
    images = models.ManyToManyField(Image, blank=True, related_name="products")
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")
    categories = models.ManyToManyField(Category, related_name="products", blank=True)

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        ordering = ["title"]


class Key(models.Model):
    key = models.CharField(max_length=64, unique=True)
    values = models.ManyToManyField("Value", through="KeyValue")

    def __str__(self):
        return f"{self.key}"
    
    class Meta:
        ordering = ["key"]


class Value(models.Model):
    value = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.value}"
    
    class Meta:
        ordering = ["value"]


class KeyValue(models.Model):
    key = models.ForeignKey(Key, on_delete=models.CASCADE)
    value = models.ForeignKey(Value, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.key.key} {self.value.value}"
    
    class Meta:
        verbose_name_plural = "Key-Value-Pairs"


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variations")
    price = models.DecimalField(
        default=1,
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )
    unit = models.CharField(max_length=10, default="Kg")
    availability = models.BooleanField(default=True)
    info = models.TextField(max_length=1000, blank=True, null=True)
    keyvalues = models.ManyToManyField(KeyValue, blank=True)
    images = models.ManyToManyField(Image, blank=True, related_name="variations")
    created = models.DateTimeField(auto_now_add=True)
    inventory = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.title} | Rs. {self.price}/-"
    
    class Meta:
        ordering = ["product"]

class Discount(models.Model):
    code = models.CharField(max_length=10, unique=True)
    percent = models.IntegerField()

    def __str__(self):
        return f"{self.code} - {self.percent}%"


class Order(models.Model):
    OPEN = 'O'
    CLOSED = 'C'
    CANCELLED = 'N'
    PENDING_CANCELLATION = 'P'
    FAILED = 'F'

    ORDER_STATUS_CHOICES = [
        (OPEN, "OPEN"),
        (CLOSED, "CLOSED"),
        (CANCELLED, "CANCELLED"),
        (PENDING_CANCELLATION, "PENDING_CANCELLATION"),
        (FAILED, "FAILED")
    ]

    customer = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(1)])
    discount = models.ForeignKey(Discount, on_delete=models.PROTECT, blank=True, null=True, related_name="orders")
    amount_payable = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(1)])
    status = models.CharField(max_length=1, choices=ORDER_STATUS_CHOICES, default=OPEN)
    placed_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    preferred_delivery_time = models.DateTimeField(blank=True, null=True)
    additional_info = models.CharField(max_length=1000, blank=True, null=True)
    count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.id}"
    
    class Meta:
        ordering = ["-placed_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="orderitems")
    product = models.ForeignKey(Variation, on_delete=models.PROTECT, related_name="orderitems")
    quantity = models.DecimalField(max_digits=6, decimal_places=2)
    unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    amount = models.DecimalField(max_digits=20, decimal_places=2)


class OrderCancellation(models.Model):
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="cancellation")
    reason = models.CharField(max_length=1000, blank=True, null=True)
    cancelled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cancelled_at"]