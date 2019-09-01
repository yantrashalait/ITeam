from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from product.models import Category, Brand, Type, Product, Notification, WaitList, Favourite, BannerImage
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .forms import ProductForm, ProductImageForm, ProductSpecificationFormset, ProductImageFormset, CategoryForm, BannerImageForm, BrandForm, TypeForm
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'


class ProductCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('add_product')
    model = Product
    template_name = 'dashboard/add_product.html'
    form_class = ProductForm

    def get_context_data(self, *args, **kwargs):
        context = super(ProductCreate, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['imageform'] = ProductImageFormset(self.request.POST, self.request.FILES, prefix='imageform')
            context['specificationform'] = ProductSpecificationFormset(self.request.POST, self.request.FILES, prefix='specform')
        
        else:
            context['imageform'] = ProductImageFormset(prefix='imageform')
            context['specificationform'] = ProductSpecificationFormset(prefix='specform')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        imageform = context['imageform']
        specificationform = context['specificationform']
        if imageform.is_valid() and specificationform.is_valid():
            self.object = form.save()
            for form in imageform:
                f = form.save(commit=False)
                f.product = self.object
                f.save()
            for form in specificationform:
                f = form.save(commit=False)
                f.product = self.object
                f.save()
            return HttpResponseRedirect('/')
        return super().form_valid(form)


class ProductUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_product'
    template_name = 'dashboard/add_product.html'
    form_class = ProductForm
    is_update_view = True

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Product, pk=id_)
    
    def get_context_data(self, *args, **kwargs):
        context = super(ProductUpdate, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['imageform'] = ProductImageFormset(self.request.POST, self.request.FILES, prefix='imageform', instance=self.object)
            context['specificationform'] = ProductSpecificationFormset(self.request.POST, self.request.FILES, prefix='specform', instance=self.object)
        
        else:
            context['imageform'] = ProductImageFormset(instance=self.object, prefix='imageform')
            context['specificationform'] = ProductSpecificationFormset(instance=self.object, prefix='specform')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        imageform = context['imageform']
        specificationform = context['specificationform']
        self.object = form.save()
        if imageform.is_valid() and specificationform.is_valid():
            for form in imageform:
                f = form.save(commit=False)
                f.product = self.object
                f.save()
            for form in specificationform:
                f = form.save(commit=False)
                f.product = self.object
                f.save()
            return HttpResponseRedirect('/')
        return super().form_valid(form)


class ProductDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'delete_product'
    template_name = 'dashboard/product_delete.html'
    form_class = ProductForm

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Product, pk=id_)
    
    def get_success_url(self):
        return reverse('product:product-list')

class CategoryList(ListView):
    template_name = 'dashboard/category_list.html'
    model = Category
    context_object_name = 'category'

class CategoryCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_category'
    model = Category
    template_name = 'dashboard/category_create.html'
    form_class = CategoryForm

    def get_success_url(self):
        return reverse('dashboard:category-list')
    
class CategoryDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'delete_category'
    model = Category
    template_name = 'dashboard/category_confirm_delete.html'
    success_url = "/dashboard/category/list"


class CategoryUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_category'
    template_name = 'dashboard/category_create.html'
    form_class = CategoryForm

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Category, pk=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:category-list')

class BrandList(ListView):
    template_name = 'dashboard/brand_list.html'
    model = Brand
    context_object_name = 'brand'

class BrandCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_brand'
    model = Brand
    template_name = 'dashboard/brand_create.html'
    form_class = BrandForm

    def get_success_url(self):
        return reverse('dashboard:brand-list')

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

class BrandDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'delete_brand'
    template_name = 'dashboard/brand_confirm_delete.html'
    model = Brand
    success_url = '/dashboard/brand/list'

class BrandUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_brand'
    template_name = 'dashboard/brand_create.html'
    form_class = BrandForm

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Brand, pk=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:brand-list')

class TypeList(ListView):
    template_name = 'dashboard/type_list.html'
    model = Type
    context_object_name = 'type'

class TypeCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_type'
    model = Type
    template_name = 'dashboard/type_create.html'
    form_class = TypeForm

    def get_success_url(self):
        return reverse('dashboard:type-list')

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

class TypeDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'delete_type'
    model = Type
    template_name = 'dashboard/type_confirm_delete.html'
    success_url = "/dashboard/type/list"

class TypeUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_type'
    template_name = 'dashboard/type_create.html'
    form_class = TypeForm

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Type, pk=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:type-list')

class BannerList(ListView):
    template_name = 'dashboard/banner_list.html'
    model = BannerImage
    context_object_name = 'banner'

class BannerCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_bannerimage'
    model = BannerImage
    template_name = 'dashboard/banner_create.html'
    form_class = BannerImageForm

    def get_success_url(self):
        return reverse('dashboard:banner-list')

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

class BannerDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'delete_banner'
    model = BannerImage
    template_name = 'dashboard/banner_confirm_delete.html'
    success_url = "/dashboard/banner/list"

class BannerUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_bannerimage'
    template_name = 'dashboard/banner_create.html'
    form_class = BannerImageForm

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(BannerImage, pk=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:banner-list')
