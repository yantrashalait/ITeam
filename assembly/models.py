from django.db import models
from django.conf import settings


class AssemblyComponent(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Accessory(models.Model):
    category = models.ForeignKey(AssemblyComponent, related_name="accessories", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    old_price = models.CharField(max_length=255, null=True, blank=True)
    new_price = models.CharField(max_length=255)
    views = models.IntegerField(default=0)
    availability = models.BooleanField(default=True)
    visibility = models.BooleanField(default=True)
    image = models.ImageField(upload_to="accessories/")
    use_in_assembly = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserAssemblyCart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="assembly_cart", on_delete=models.CASCADE)
    accessories = models.ManyToManyField(Accessory, related_name="user_assembly")
    total_price = models.FloatField()
    added_date = models.DateTimeField(auto_now_add=True)
    checked_out = models.BooleanField(default=False)


class UserAssemblyOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="assembly_order", on_delete=models.CASCADE)
    cart = models.ManyToManyField(UserAssemblyCart, related_name="orders")
    note = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    total_price = models.FloatField()
    approved = models.BooleanField(default=False)
    decline = models.BooleanField(default=False)
    declined_reason = models.TextField(null=True, blank=True)
    delivered = models.BooleanField(default=False)
