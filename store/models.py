from django.db import models
from django.contrib.auth.models import User


# Category model
class Category(models.Model):
    name = models.CharField(max_length = 100)
    image = models.ImageField(upload_to = 'categories/', blank = True, null = True)
    slug = models.SlugField(unique = True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

# Products model
class Product(models.Model):
    name = models.CharField(max_length = 200)
    category = models.ForeignKey(Category, on_delete = models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    description = models.TextField(blank = True)
    image = models.ImageField(upload_to = 'products/', blank = True, null = True)
    stock = models.PositiveIntegerField(default = 0)
    discount = models.PositiveIntegerField(default = 0, help_text = 'Discount percentage')
    is_active = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        if self.discount:
            return round(self.price - (self.price * self.discount / 100), 2)
        return self.price

    @property
    def in_stock(self):
        return self.stock > 0

# Address model
class Address(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'addresses')
    house_no = models.CharField(max_length = 100)
    street = models.CharField(max_length = 200)
    city = models.CharField(max_length = 100)
    pincode = models.CharField(max_length = 10)
    is_default = models.BooleanField(default = False)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.house_no}, {self.street}, {self.city} - {self.pincode}"

# Cart model 
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'cart')
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()

# CartItem model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE, related_name = 'items')
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField(default = 1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.discounted_price * self.quantity

# Wishlist model
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'wishlist')
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    added_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

# Coupon Model
class Coupon(models.Model):
    code = models.CharField(max_length = 50, unique = True)
    discount_percent = models.PositiveIntegerField()
    active = models.BooleanField(default = True)
    min_order_amount = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0)

    def __str__(self):
        return self.code

# Order model
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'orders')
    address = models.ForeignKey(Address, on_delete = models.SET_NULL, null = True)
    total_price = models.DecimalField(max_digits = 10, decimal_places = 2)
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default = 'pending')
    coupon = models.ForeignKey(Coupon, on_delete = models.SET_NULL, null = True, blank = True)
    discount_amount = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0)
    created_at = models.DateTimeField(auto_now_add = True)
    estimated_delivery = models.CharField(max_length = 50, default = '10-20 minutes')

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE, related_name = 'items')
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits = 10, decimal_places = 2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = 'reviews')
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    rating = models.PositiveIntegerField(choices = [(i, i) for i in range(1, 6)])
    comment = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"




