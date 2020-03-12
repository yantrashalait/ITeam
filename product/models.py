from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from django.urls import reverse
from django.core.mail import send_mail


class Category(models.Model):
    name = models.CharField(max_length=100)
    category_image = models.ImageField(upload_to='category/', null=True, blank=True, help_text='Image Size: width=410px, height=281px')

    def __str__(self):
        return self.name


class Brand(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='brands')
    name = models.CharField(max_length=100)
    brand_image = models.ImageField(upload_to='brands/', null=True, blank=True, help_text="Image size: width=193px height=115px")

    def __str__(self):
        return self.name


class Type(models.Model):
    brand_type = models.CharField(max_length=100, help_text="E.g. Economic, Gaming, etc.")

    def __str__(self):
        return self.brand_type


# class Color(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name


class Product(models.Model):
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    previous_price = models.CharField(max_length=100, help_text=('e.g., Rs. 150000'), null=True, blank=True)
    new_price = models.CharField(max_length=100, help_text=('e.g., Rs. 150000'), null=True, blank=True)
    category = models.ForeignKey(Category, verbose_name='Category', on_delete=models.CASCADE, related_name='product_category')
    brand = models.ForeignKey(Brand, verbose_name='Brand', on_delete=models.CASCADE, related_name='product_brand')
    product_type = models.ForeignKey(Type, verbose_name='Type of laptop', on_delete=models.CASCADE, related_name='product_type', null=True, blank=True)
    views = models.IntegerField(default=0)
    super_deals = models.BooleanField(default=False, verbose_name='Do you want this item to display in super deals section?')
    offer = models.BooleanField(default=False, verbose_name='Does you want this item to be displayed in offer section?')
    availability = models.BooleanField(default=True, verbose_name='Is this product available in stock?')
    main_image = models.ImageField(upload_to='products/', null=True, blank=True, help_text="Image size: width=265px height=290px")
    offer_tag = models.CharField(max_length=100, null=True, blank=True, help_text="E.g. 15% off")
    visibility = models.BooleanField(default=True, verbose_name="Make this product visibile?")

    def __str__(self):
        return self.name

    def save(self):
        if self.previous_price and self.previous_price > self.new_price:
            offer = round(((int(self.previous_price) - int(self.new_price)) / int(self.previous_price)), 2)* 100
            self.offer_tag = offer
        super(Product, self).save()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    big_image = models.ImageField(upload_to='products/big/', null=True, blank=True, help_text="Image size: width=700 px height=700px")
    thumbnail_image = models.ImageField(upload_to='products/thumbnail/', null=True, blank=True, help_text="Image size: width=100px height=100px")


class BannerImage(models.Model):
    image = models.ImageField(upload_to='banners/', help_text="Image size: width=1280px height=435px")


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notification', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    is_seen = models.BooleanField(default=False)


class WaitList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='waitlist', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='waitlist', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    removed = models.BooleanField(default=False)
    removed_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + ' ' + self.product.name


class Favourite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='favourite', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='favourite', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' ' + self.product.name


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='cart', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart', on_delete=models.CASCADE)
    amount = models.IntegerField(null=True, blank=True)
    total_price = models.FloatField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    removed = models.BooleanField(default=False)
    removed_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + ' ' + self.product.name


class UserBargain(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bargain', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='bargain', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' ' + self.product.name


class UserRequestProduct(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    product_name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=100, help_text=('e.g., Laptop, Desktop'),  null=True, blank=True)
    specification = models.TextField()
    contact_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=100,  null=True, blank=True)
    name = models.CharField(max_length=100,  null=True, blank=True)
    active = models.BooleanField(default=False)
    amount = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name + ' ' + self.product_name


class SuperImage(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, help_text="Insert name to avoid confusion")
    super_image = models.ImageField(upload_to='super/', help_text="Image size: width: 401px height: 424px")

    def __str__(self):
        return self.name


class OfferImage(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, help_text="Insert name to avoid confusion")
    offer_image = models.ImageField(upload_to='offers/', help_text="Image size: width: 401px height: 424px")

    def __str__(self):
        return self.name


class Subscription(models.Model):
    email = models.EmailField(max_length=70, null=True, blank=True, unique=True)

    def __str__(self):
        return self.email


class UserOrder(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE)
    cart = models.ManyToManyField(Cart, related_name="orders")
    total_price = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(default=datetime.now)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    note = models.TextField()

    def __str__(self):
        return self.user.username


class SpecificationTitle(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class SpecificationContent(models.Model):
    title = models.ForeignKey(SpecificationTitle, on_delete=models.CASCADE, related_name="content")
    content = models.CharField(max_length=255)

    def __str__(self):
        return self.content


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    title = models.ForeignKey(SpecificationTitle, on_delete=models.CASCADE, related_name="product_title")
    content = models.ForeignKey(SpecificationContent, on_delete=models.CASCADE, related_name="product_content")


class AboutITeam(models.Model):
    contact1 = models.CharField(max_length=100, default='')
    contact2 = models.CharField(max_length=100, null=True, blank=True)
    contact3 = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="logo/", help_text="Image size: width=192px height=31px")
    address = models.CharField(max_length=255, null=True, blank=True)
    facebook_link = models.CharField(max_length=255, null=True, blank=True)
    instagram_link = models.CharField(max_length=255, null=True, blank=True)
    youtube_link = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email


@receiver(post_save, sender=Product)
def product_notify(sender, instance, created, **kwargs):
    # check if the product is made available and user have added it to their wish list
    if instance.availability == True:
        if WaitList.objects.filter(product=instance).exists():
            user_mail = []
            users = WaitList.objects.filter(product=instance)
            for item in users:
                user_mail.append(item.user.email)
                if not Notification.objects.filter(user=item.user, product=item.product).exists():
                    Notification.objects.create(
                        user=item.user,
                        date=datetime.now(),
                        product = item.product,
                        title='Product Available',
                        description='Product ' + item.product.name + ' is available on stock now.')
            # send_mail(
            #     'Product Available',
            #     'Product' + instance.name + 'is not available on stock.',
            #     'support@iteam.com.np',
            #     [user_mail],
            #     fail_silently=False
            # )


    # check if price has reduced
    if instance.previous_price:
        if instance.new_price < instance.previous_price:
            if UserBargain.objects.filter(product=instance).exists():
                users = UserBargain.objects.filter(product=instance)
                for item in users:
                    if not Notification.objects.filter(user=item.user, product = item.product).exists():
                        Notification.objects.create(
                                user=item.user,
                                date=datetime.now(),
                                product = item.product,
                                title='Price Drop',
                                description='Product ' + item.product.name + ' is now available at ' + instance.new_price)
