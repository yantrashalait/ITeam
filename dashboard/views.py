from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.html import escape
from django.db import transaction

from product.models import Category, Brand, Type, Product, Notification, WaitList, Favourite, BannerImage, \
    SuperImage, OfferImage, UserBargain, UserRequestProduct, UserOrder, SpecificationTitle, AboutITeam, Cart, \
    SpecificationContent, ProductImage, ProductSpecification
from .forms import ProductForm, ProductImageForm, ProductSpecificationFormset, ProductImageFormset, \
    CategoryForm, BannerImageForm, BrandForm, TypeForm, SuperImageForm, OfferImageForm, \
    SpecificationContentFormset, SpecificationTitleForm, SpecificationContentForm, AboutForm
from assembly.models import AssemblyComponent, Accessory
from assembly.forms import AssemblyComponentForm, AccessoryForm


def handlePopAdd(request, addForm, field):
    if request.method == "POST":
        form = addForm(request.POST)
        if form.is_valid():
            try:
                newObject = form.save()
            except form.ValidationError:
                newObject = None
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % (escape(newObject._get_pk_val()), escape(newObject)))
        else:
            print(form.errors)
    else:
        form = addForm()

    return render(request, "add/popadd.html", {'form': form, 'field': field})


def brandPopAdd(request, addForm, field):
    if request.method == "POST":
        form = addForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                newObject = form.save()
            except form.ValidationError:
                newObject = None
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % (escape(newObject._get_pk_val()), escape(newObject)))
        else:
            print('not valid')
            print(form.errors)
    else:
        form = addForm()
    return render(request, "add/brand-popadd.html", {'form': form, 'field': field})


def categoryPopAdd(request, addForm, field):
    if request.method == "POST":
        form = addForm(request.POST)
        print(form)
        if form.is_valid():
            try:
                newObject = form.save()
            except form.ValidationError:
                newObject = None
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % (escape(newObject._get_pk_val()), escape(newObject)))
        else:
            print('not valid')
            print(form.errors)
    else:
        form = addForm()
    return render(request, "add/category-popadd.html", {'form': form, 'field': field})


class DashboardView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_product'
    template_name = 'dashboard/product-list.html'
    model = Product
    context_object_name = 'product'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        return Product.objects.all().order_by('-id')


class ProductList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_product'
    template_name = 'dashboard/product-list.html'
    model = Product
    context_object_name = 'product'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        return Product.objects.all().order_by('-id')


@login_required
def newBrand(request, *args, **kwargs):
    return brandPopAdd(request, BrandForm, "brand")


@login_required
def newType(request, *args, **kwargs):
    return handlePopAdd(request, TypeForm, "product_type")


@login_required
def newCategory(request, *args, **kwargs):
    return categoryPopAdd(request, AssemblyComponentForm, "category")


class ProductCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('add_product')
    model = Product
    template_name = 'dashboard/add-product.html'
    form_class = ProductForm

    def get_context_data(self, *args, **kwargs):
        context = super(ProductCreate, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['imageform'] = ProductImageFormset(self.request.POST, self.request.FILES, prefix='imageform', instance=self.object)
            context['specificationform'] = ProductSpecificationFormset(self.request.POST, self.request.FILES, prefix='specform', instance=self.object)

        else:
            context['imageform'] = ProductImageFormset(prefix='imageform', instance=self.object)
            context['specificationform'] = ProductSpecificationFormset(prefix='specform', instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        imageform = context['imageform']
        specificationform = context['specificationform']
        with transaction.atomic():
            self.object = form.save()
            if imageform.is_valid() and specificationform.is_valid():
                for form in imageform:
                    if form.cleaned_data.get('big_image') and form.cleaned_data.get('thumbnail_image'):
                        f = form.save(commit=False)
                        f.product = self.object
                        f.save()
                for form in specificationform:
                    if form.cleaned_data.get('title'):
                        f = form.save(commit=False)
                        f.product = self.object
                        f.save()
                return HttpResponseRedirect('/dashboard/product/list/')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:product-list')


class ProductUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_product'
    template_name = 'dashboard/add-product.html'
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

        if imageform.is_valid():
            for form in imageform:
                if form.cleaned_data.get('big_image') and form.cleaned_data.get('thumbnail_image'):
                    f = form.save(commit=False)
                    f.product = self.object
                    f.save()

        if specificationform.is_valid():
            for form in specificationform:
                if form.cleaned_data.get('title'):
                    f = form.save(commit=False)
                    f.product = self.object
                    f.save()
            return HttpResponseRedirect('/dashboard/product/list/')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:product-list')


class ProductDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'delete_product'
    model = Product
    template_name = 'dashboard/product_confirm_delete.html'
    success_url = "/dashboard/product/list"


class CategoryList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_category'
    template_name = 'dashboard/category-list.html'
    model = Category
    context_object_name = 'category'
    paginate_by = 10


class CategoryCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_category'
    model = Category
    template_name = 'dashboard/add-category.html'
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
    template_name = 'dashboard/add-category.html'
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
    template_name = 'dashboard/brand-list.html'
    model = Brand
    context_object_name = 'brand'
    paginate_by = 10


class BrandCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_brand'
    model = Brand
    template_name = 'dashboard/add-brand.html'
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
    template_name = 'dashboard/add-brand.html'
    form_class = BrandForm

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Brand, pk=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:brand-list')


class TypeList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_type'
    template_name = 'dashboard/type-list.html'
    model = Type
    context_object_name = 'type'
    paginate_by = 10


class TypeCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_type'
    model = Type
    template_name = 'dashboard/add-type.html'
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
    template_name = 'dashboard/add-type.html'
    form_class = TypeForm

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Type, pk=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:type-list')


class BannerList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_bannerimage'
    template_name = 'dashboard/banner-list.html'
    model = BannerImage
    context_object_name = 'banner'
    paginate_by = 10


class BannerCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_bannerimage'
    model = BannerImage
    template_name = 'dashboard/add-banner.html'
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
    template_name = 'dashboard/add-banner.html'
    form_class = BannerImageForm

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(BannerImage, pk=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:banner-list')


class SuperImageList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_superimage'
    template_name = 'dashboard/super-list.html'
    model = SuperImage
    context_object_name = 'superimage'
    paginate_by = 10


class SuperImageAdd(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_superimage'
    template_name = 'dashboard/add-super.html'
    form_class = SuperImageForm

    def get_success_url(self):
        return reverse('dashboard:superimage-list')

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


class SuperImageUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_superimage'
    template_name = 'dashboard/add-super.html'
    form_class = SuperImageForm

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(SuperImage, pk=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:superimage-list')


class SuperImageDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'delete_offerimage'
    model = SuperImage
    template_name = 'dashboard/superimage_confirm_delete.html'
    success_url = "/dashboard/superimage/list"


class OfferImageList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_offerimage'
    template_name = 'dashboard/offer-list.html'
    model = OfferImage
    context_object_name = 'offerimage'
    paginate_by = 10


class OfferImageAdd(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_offerimage'
    template_name = 'dashboard/add-offer.html'
    form_class = OfferImageForm

    def get_success_url(self):
        return reverse('dashboard:offerimage-list')

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


class OfferImageUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_offerimage'
    template_name = 'dashboard/add-offer.html'
    form_class = OfferImageForm

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(OfferImage, pk=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:offerimage-list')


class OfferImageDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'delete_offerimage'
    model = OfferImage
    template_name = 'dashboard/offerimage_confirm_delete.html'
    success_url = "/dashboard/offerimage/list"


class OrderList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_product'
    model = UserOrder
    template_name = 'dashboard/order-list.html'
    context_object_name = 'order'

    def get_context_data(self, *args, **kwargs):
        context = super(OrderList, self).get_context_data(**kwargs)
        requests = UserRequestProduct.objects.filter(active=True).order_by('-date')
        bargains = UserBargain.objects.all()
        context['requests'] = requests
        context['bargains'] = bargains
        return context

    def get_queryset(self, *args, **kwargs):
        return UserOrder.objects.all().order_by('-date')


class OrderDetail(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'add_product'
    template_name = 'dashboard/order-detail.html'

    def get_context_data(self, *args ,**kwargs):
        context = super(OrderDetail, self).get_context_data(**kwargs)
        _id = self.kwargs.get('pk')
        order = UserOrder.objects.get(id=_id)
        context['carts'] = order.cart.all()
        return context


class SpecificationCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('add_product')
    model = SpecificationTitle
    template_name = 'dashboard/add-specification.html'
    form_class = SpecificationTitleForm

    def get_context_data(self, *args, **kwargs):
        context = super(SpecificationCreate, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['contentform'] = SpecificationContentFormset(self.request.POST)
        else:
            context['contentform'] = SpecificationContentFormset()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        contentform = context['contentform']
        if contentform.is_valid():
            self.object = form.save()
            for form in contentform:
                content = form.cleaned_data.get('content')
                if content != '' and content != None and content != ' ':
                    f = form.save(commit=False)
                    f.title = self.object
                    f.save()
            return HttpResponseRedirect('/dashboard/specification/list')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:specification-list')


class SpecificationUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_product'
    template_name = 'dashboard/add-specification.html'
    form_class = SpecificationTitleForm
    is_update_view = True

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(SpecificationTitle, pk=id_)

    def get_context_data(self, *args, **kwargs):
        context = super(SpecificationUpdate, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['contentform'] = SpecificationContentFormset(self.request.POST, instance=self.object)

        else:
            context['contentform'] = SpecificationContentFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        contentform = context['contentform']
        self.object = form.save()

        if contentform.is_valid():
            for form in contentform:
                content = form.cleaned_data.get('content')
                if content != '' and content != None and content != ' ':
                    f = form.save(commit=False)
                    f.title = self.object
                    f.save()
            return HttpResponseRedirect('/dashboard/specification/list')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:specification-list')


class SpecificationList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_product'
    model = SpecificationTitle
    template_name = 'dashboard/specification-list.html'
    context_object_name = 'spec'
    paginate_by = 10


class SpecificationDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'delete_product'
    model = SpecificationTitle
    template_name = 'dashboard/specification_confirm_delete.html'
    success_url = "/dashboard/specification/list"


class SpecificationContentList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_product'
    model = SpecificationContent
    template_name = "dashboard/spec-content-list.html"
    context_object_name = 'spec_content'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.filter(title_id=self.kwargs.get('pk'))


class SpecificationContentDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "delete_product"
    model = SpecificationContent
    template_name = "dashboard/specification_content_confirm_delete.html"

    def get_success_url(self, *args, **kwargs):
        return reverse('dashboard:specification-content-list', kwargs={'pk': self.kwargs.get('spec_id')})


@login_required
def newSpecificationTitle(request, *args, **kwargs):
    return handlePopAdd(request, SpecificationTitleForm, "title")


@login_required
def newSpecificationContent(request, *args, **kwargs):
    return handlePopAdd(request, SpecificationContentForm, "content")


class AboutCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_aboutiteam'
    model = AboutITeam
    template_name = 'dashboard/about-iteam.html'
    form_class = AboutForm

    def get_success_url(self):
        return reverse('dashboard:dashboard')


class AboutUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'change_aboutiteam'
    template_name = 'dashboard/about-iteam.html'
    form_class = AboutForm

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(AboutITeam, pk=id_)

    def get_success_url(self):
        return reverse('dashboard:dashboard')


class ProductImageList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_product'
    template_name = 'dashboard/product-image-list.html'
    model = ProductImage
    context_object_name = 'images'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.filter(product_id=self.kwargs.get('pk'))


class ProductImageDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'delete_product'
    template_name = 'dashboard/product_image_confirm_delete.html'
    model = ProductImage

    def get_success_url(self, *args, **kwargs):
        return reverse('dashboard:product-images-list', kwargs={'pk': self.kwargs.get('product_id')})


class ProductSpecificationList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'add_product'
    template_name = 'dashboard/product-specification-list.html'
    model = ProductSpecification
    context_object_name = 'spec'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.filter(product__id=self.kwargs.get('pk'))


class ProductSpecificationDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'delete_product'
    template_name = 'dashboard/product_specification_confirm_delete.html'
    model = ProductSpecification

    def get_success_url(self, *args, **kwargs):
        return reverse('dashboard:product-specification-list', kwargs={'pk': self.kwargs.get('product_id')})


class AssemblyComponentCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_product'
    template_name = 'dashboard/assembly_component_form.html'
    model = AssemblyComponent
    form_class = AssemblyComponentForm

    def get_success_url(self):
        return reverse('dashboard:assembly-component-list')


class AssemblyComponentList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "add_product"
    template_name = "dashboard/assembly_component_list.html"
    model = AssemblyComponent
    paginate_by = 10
    context_object_name = "components"


class AssemblyComponentEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "add_product"
    template_name = "dashboard/assembly_component_form.html"
    model = AssemblyComponent
    form_class = AssemblyComponentForm

    def get_object(self, queryset=None):
        _id = self.kwargs.get('pk', 1)
        return get_object_or_404(self.model, pk=_id)

    def get_success_url(self):
        return reverse("dashboard:assembly-component-list")


class AssemblyComponentDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "add_product"
    template_name = "dashboard/assembly_component_delete.html"
    model = AssemblyComponent
    success_url = "/dashboard/assembly-component/list"


class AccessoryCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'add_product'
    template_name = "dashboard/accessory-form.html"
    model = Accessory
    form_class = AccessoryForm

    def get_success_url(self):
        return reverse('dashboard:accessory-list')


class AccessoryList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "add_product"
    template_name = "dashboard/accessory-list.html"
    model = Accessory
    paginate_by = 10
    context_object_name = "accessories"


class AccessoryEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "add_product"
    template_name = "dashboard/accessory-form.html"
    model = Accessory
    form_class = AccessoryForm

    def get_success_url(self):
        return reverse("dashboard:accessory-list")


class AccessoryDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "add_product"
    template_name = "dashboard/accessory-delete.html"
    model = Accessory
    success_url = "/dashboard/accessory/list"
