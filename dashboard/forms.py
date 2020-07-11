from django import forms
from product.models import Product, Category, Brand, Type, BannerImage, Cart, ProductSpecification, \
    ProductImage, SuperImage, OfferImage, SpecificationTitle, SpecificationContent, AboutITeam
from django.forms.models import inlineformset_factory
from PIL import Image
from .widgets import *


class ProductForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)
    brand = forms.ModelChoiceField(Brand.objects, widget=SelectWithPop)
    product_type = forms.ModelChoiceField(Type.objects, widget=SelectWithPop)

    class Meta:
        model = Product
        fields = ['name', 'description', 'previous_price', 'new_price', 'category', 'brand', 'product_type', 'super_deals', 'offer', 'availability', 'main_image', 'visibility', 'x', 'y', 'width', 'height']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(**kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['previous_price'].widget.attrs['class'] = 'form-control'
        self.fields['new_price'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['brand'].widget.attrs['class'] = 'form-control'
        self.fields['product_type'].widget.attrs['class'] = 'form-control'
        self.fields['super_deals'].widget.attrs['class'] = 'form-control'
        self.fields['offer'].widget.attrs['class'] = 'form-control'
        self.fields['availability'].widget.attrs['class'] = 'form-control'
        self.fields['main_image'].widget.attrs['class'] = 'form-control'
        self.fields['visibility'].widget.attrs['class'] = 'form-control'

    def save(self):
        photo = super(ProductForm, self).save()
        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        if x is not None and y is not None:
            image = Image.open(photo.main_image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((265, 290), Image.ANTIALIAS)
            resized_image.save(photo.main_image.path)
        return photo


class CategoryForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ['name', 'category_image', 'x', 'y', 'width', 'height']

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['category_image'].widget.attrs['class'] = 'form-control'

    def save(self):
        photo = super(CategoryForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        if x is not None and y is not None:
            image = Image.open(photo.category_image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((410, 281), Image.ANTIALIAS)
            resized_image.save(photo.category_image.path)
        return photo


class BrandForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Brand
        fields = ['category', 'name', 'brand_image', 'x', 'y', 'width', 'height']

    # def __init__(self, *args, **kwargs):
    #     super(BrandForm, self).__init__(**kwargs)
    #     self.fields['name'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['category'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['brand_image'].widget.attrs.update({'class': 'form-control'})

    def save(self):
        photo = super(BrandForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        if x is not None and y is not None:
            image = Image.open(photo.brand_image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((193, 115), Image.ANTIALIAS)
            resized_image.save(photo.brand_image.path)
        return photo


class TypeForm(forms.ModelForm):
    class Meta:
        model = Type
        fields = ('brand_type', )
    
    def __init__(self, *args, **kwargs):
        super(TypeForm, self).__init__(**kwargs)
        self.fields['brand_type'].widget.attrs.update({'class': 'form-control'})


class BannerImageForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = BannerImage
        fields = ['image', 'x', 'y', 'width', 'height']

    def __init__(self, *args, **kwargs):
        super(BannerImageForm, self).__init__(**kwargs)
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

    def save(self, *args, **kwargs):
        photo = super(BannerImageForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        if x is not None and y is not None:
            image = Image.open(photo.image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((1280, 435), Image.ANTIALIAS)
            resized_image.save(photo.image.path)
        return photo


class ProductSpecificationForm(forms.ModelForm):
    title = forms.ModelChoiceField(SpecificationTitle.objects, widget=SelectWithPop)
    content = forms.ModelChoiceField(SpecificationContent.objects, widget=SelectWithPop)

    class Meta:
        model = ProductSpecification
        fields = ['title', 'content']


class ProductImageForm(forms.ModelForm):
    x_main = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y_main = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width_main = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height_main = forms.FloatField(widget=forms.HiddenInput(), required=False)

    x_thumb = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y_thumb = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width_thumb = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height_thumb = forms.FloatField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(ProductImageForm, self).__init__(*args, **kwargs)
        self.fields['big_image'].widget.attrs.update({'class': 'big_image_class'})
        self.fields['thumbnail_image'].widget.attrs.update({'class': 'thumb_image_class'})

    class Meta:
        model = ProductImage
        fields = ['big_image', 'thumbnail_image', 'x_main', 'y_main', 'width_main', 'height_main', 'x_thumb', 'y_thumb', 'width_thumb', 'height_thumb']

    def save(self, commit=True):
        photo = super(ProductImageForm, self).save(commit=False)

        x_main = self.cleaned_data.get('x_main')
        y_main = self.cleaned_data.get('y_main')
        w_main = self.cleaned_data.get('width_main')
        h_main = self.cleaned_data.get('height_main')

        x_thumb = self.cleaned_data.get('x_thumb')
        y_thumb = self.cleaned_data.get('y_thumb')
        w_thumb = self.cleaned_data.get('width_thumb')
        h_thumb = self.cleaned_data.get('height_thumb')

        if x_main is not None and y_main is not None:
            image = Image.open(photo.big_image)
            cropped_image = image.crop((x_main, y_main, w_main+x_main, h_main+y_main))
            resized_image = cropped_image.resize((700, 700), Image.ANTIALIAS)
            resized_image.save(photo.big_image.path)

        if x_thumb is not None and y_thumb is not None:
            image = Image.open(photo.thumbnail_image)
            cropped_image = image.crop((x_thumb, y_thumb, w_thumb + x_thumb, h_thumb + y_thumb))
            resized_image = cropped_image.resize((100, 100), Image.ANTIALIAS)
            resized_image.save(photo.thumbnail_image.path)
        if commit:
            photo.save()
        else:
            return photo


ProductImageFormset = inlineformset_factory(Product, ProductImage, form=ProductImageForm, fields=['big_image', 'thumbnail_image', 'x_main', 'y_main', 'width_main', 'height_main', 'x_thumb', 'y_thumb', 'width_thumb', 'height_thumb'], extra=1, max_num=10)
ProductSpecificationFormset = inlineformset_factory(Product, ProductSpecification, form=ProductSpecificationForm, fields=['title', 'content'], extra=1, max_num=20)


class SuperImageForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = SuperImage
        fields = ['name', 'super_image', 'x', 'y', 'width', 'height']

    def __init__(self, *args, **kwargs):
        super(SuperImageForm, self).__init__(**kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['super_image'].widget.attrs['class'] = 'form-control'

    def save(self):
        photo = super(SuperImageForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        if x is not None and y is not None:
            image = Image.open(photo.super_image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((401, 424), Image.ANTIALIAS)
            resized_image.save(photo.super_image.path)
        return photo


class OfferImageForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = OfferImage
        fields = ['name', 'offer_image', 'x', 'y', 'width', 'height']

    def __init__(self, *args, **kwargs):
        super(OfferImageForm, self).__init__(**kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['offer_image'].widget.attrs['class'] = 'form-control'

    def save(self):
        photo = super(OfferImageForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        if x is not None and y is not None:
            image = Image.open(photo.offer_image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((401, 424), Image.ANTIALIAS)
            resized_image.save(photo.offer_image.path)
        return photo


class SpecificationTitleForm(forms.ModelForm):
    class Meta:
        model = SpecificationTitle
        fields = ('title',)


class SpecificationContentForm(forms.ModelForm):
    class Meta:
        model = SpecificationContent
        fields = ('title', 'content')


SpecificationContentFormset = inlineformset_factory(SpecificationTitle, SpecificationContent, form=SpecificationContentForm, fields=['title', 'content'], extra=1, max_num=20)


class AboutForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = AboutITeam
        fields = ['contact1', 'contact2', 'contact3', 'address', 'facebook_link', 'youtube_link', 'instagram_link', 'email', 'logo', 'x', 'y', 'height', 'width']

    def save(self):
        photo = super(AboutForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        if x is not None and y is not None:
            image = Image.open(photo.logo)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((192, 31), Image.ANTIALIAS)
            resized_image.save(photo.logo.path)
        return photo
