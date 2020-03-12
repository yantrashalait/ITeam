from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from .models import Product, Category, Brand, Type, BannerImage, ProductImage, ProductSpecification, Cart, Subscription, Notification, UserRequestProduct, UserOrder
from .forms import CartForm, UserRequestProductForm, UserOrderForm
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.template import RequestContext


def handler404(request, *args, **argv):
    response = render_to_response('dashboard/404.html')
    response.status_code = 404
    return response

def handler500(request, *args, **argv):
    response = render_to_response('dashboard/500.html')
    response.status_code = 500
    return response


def index(request):
    super_deals = Product.objects.filter(super_deals=True, visibility=True)
    most_viewed = Product.objects.filter(views__gte=10, visibility=True)
    offer = Product.objects.filter(offer=True, visibility=True)
    brand = Brand.objects.all()
    superimages = SuperImage.objects.last()
    offerimages = OfferImage.objects.last()
    banner = BannerImage.objects.all()
    category = Category.objects.all()
    gaming = Product.objects.filter(product_type__brand_type__icontains="gam")
    business = Product.objects.filter(product_type__brand_type__icontains="busi")
    economic = Product.objects.filter(product_type__brand_type__icontains="eco")
    return render(request, 'product/index.html', {'super_deals': super_deals, 'most_viewed':most_viewed, 'offer':offer, 'brand':brand, 'superimage': superimages, 'offerimage': offerimages, 'banner': banner, 'category': category, 'gaming': gaming, 'business': business, 'economic': economic})


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'product/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        Notification.objects.filter(is_seen=False).update(is_seen=True)
        return Notification.objects.filter(user_id=self.kwargs.get('pk')).order_by('-date')


class CartListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'product/cart.html'
    context_object_name = 'carts'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Cart.objects.filter(removed=False, product__visibility=True).order_by('-date')
        else:
            return Cart.objects.filter(user_id=self.kwargs.get('pk'), removed=False, product__visibility=True).order_by('-date')

    def post(self, request, *args, **kwargs):
        _id = self.request.POST.get('delete')
        cart = Cart.objects.get(pk=_id)
        cart.removed = True
        cart.save()
        return render(request, self.template_name, {'carts': self.get_queryset()})


class WaitListView(LoginRequiredMixin, ListView):
    model = WaitList
    template_name = 'product/wait.html'
    context_object_name = 'waitlists'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return WaitList.objects.filter(removed=False, product__visibility=True).order_by('-date')
        else:
            return WaitList.objects.filter(user_id=self.kwargs.get('pk'), removed=False).order_by('-date')

    def post(self, request, *args, **kwargs):
        _id = self.request.POST.get('delete')
        wait = WaitList.objects.get(pk=_id)
        wait.removed = True
        wait.save()
        return render(request, self.template_name, {'waitlists': self.get_queryset()})

class FavouriteListView(LoginRequiredMixin, ListView):
    model = Favourite
    template_name = 'product/fav.html'
    context_object_name = 'favourites'

    def get_queryset(self):
        return Favourite.objects.filter(user_id=self.kwargs.get('pk'), removed=False, product__visibility=True).order_by('-date')

    def post(self, request, *args, **kwargs):
        _id = self.request.POST.get('delete')
        fav = Favourite.objects.get(pk=_id)
        fav.removed=True
        fav.save()
        return render(request, self.template_name, {'favourites': self.get_queryset()})

# mark a notification as seen
def see_notification(request, *args, **kwargs):
    notification = Notification.objects.get(id=kwargs.get('pk'))
    notification.is_seen = True
    notification.save()
    return HttpResponse('notification seen')


class ProductList(ListView):
    template_name = 'product/product-list.html'
    model = Product
    context_object_name = 'product'
    paginate_by = 10
    queryset = Product.objects.filter(visibility=True)

    # def get_queryset(self):
    #     return Product.objects.all()

    def get_context_data(self,**kwargs):
        context = super(ProductList,self).get_context_data(**kwargs)
        context['types'] = Type.objects.all()
        context['brands'] = Brand.objects.all()
        return context


class ProductDetail(DetailView):
    model = Product
    template_name = 'product/product-detail.html'
    context_object_name = 'product'

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Product, pk=id_)

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        self.object.views += 1
        self.object.save()
        context['brands'] = Brand.objects.all()
        context['related'] = Product.objects.filter( ~Q(id=self.object.id), category=self.object.category, brand=self.object.brand, product_type=self.object.product_type, visibility=True)[:10]
        return context


class AddCart(LoginRequiredMixin, CreateView):
    form_class = CartForm

    def post(self, request, *args, **kwargs):
        color = request.POST.get("color")
        quantity = int(request.POST.get("quantity"))
        product_id = request.POST.get("product")
        product = Product.objects.get(id=int(product_id), visibility=True)
        cart = Cart()
        cart.amount=quantity
        cart.total_price = int(product.new_price)*quantity
        cart.user=request.user
        cart.product=product
        cart.save()
        return HttpResponseRedirect(reverse('product:cart-list', kwargs={'pk': request.user.pk}))

    def get_success_url(self):
        return reverse('product:cart-list', kwargs={'pk':self.request.user.pk})


@login_required(login_url='/login/')
def add_to_favourite(request, *args, **kwargs):
    if request.user.is_authenticated:
        if request.is_ajax():
            _id = request.GET.get('pk')
            product = Product.objects.get(id=int(_id))
            fav, created = Favourite.objects.get_or_create(product=product, user=request.user)
            if not created:
                if fav.removed == True:
                    fav.removed = False
                    fav.save()
            data = {'pk': _id}
            return HttpResponse(data)
        else:
            return HttpResponse({'message': 'Added Failed'})
    else:
        return HttpResponseRedirect('login')


@login_required(login_url='/login/')
def add_to_waitlist(request, *args, **kwargs):
    if request.user.is_authenticated:
        if request.is_ajax():
            _id = request.GET.get('pk')
            product = Product.objects.get(id=int(_id))
            wait, created = WaitList.objects.get_or_create(product=product, user=request.user)
            if not created:
                if wait.removed == True:
                    wait.removed = False
                    wait.save()
            data = {'pk': _id}
            return HttpResponse(data)
        else:
            return HttpResponse({'message': 'Added Failed'})
    else:
        return HttpResponseRedirect('login')

@login_required(login_url='/login/')
def add_to_bargain(request, *args, **kwargs):
    if request.user.is_authenticated:
        if request.is_ajax():
            _id = request.GET.get('pk')
            product = Product.objects.get(id=int(_id))
            UserBargain.objects.get_or_create(product=product, user=request.user)
            data = {'pk': _id}
            return HttpResponse(data)
        else:
            return HttpResponse({'message': 'Added Failed'})
    else:
        return HttpResponseRedirect('login')


class CategoryListView(ListView):
    template_name = 'product/product-list.html'
    model = Product
    context_object_name = 'product'
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        brands = self.request.GET.getlist('brands')
        types = self.request.GET.getlist('types')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        brand_ids = []
        type_ids = []
        for brand_id in brands:
            brand_ids.append(int(brand_id))
        for type_id in types:
            type_ids.append(int(type_id))
        try:
            if min_price.isdigit():
                min_price = int(min_price)
            else:
                min_price = None
        except:
            min_price = None
        try:
            if max_price.isdigit():
                max_price = int(max_price)
            else:
                max_price = None
        except:
            max_price = None

        if brand_ids and type_ids and min_price and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, product_type_id__in=type_ids, new_price__range=(min_price, max_price), category_id=self.kwargs.get("pk"), visibility=True)
        elif brand_ids and min_price and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__range=(min_price, max_price), category_id=self.kwargs.get("pk"), visibility=True)
        elif brand_ids and type_ids:
            return Product.objects.filter(brand_id__in=brand_ids, product_type_id__in=type_ids, category_id=self.kwargs.get("pk"), visibility=True)
        elif brand_ids and min_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__gte=min_price, category_id=self.kwargs.get("pk"), visibility=True)
        elif brand_ids and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__lte=max_price, category_id=self.kwargs.get("pk"), visibility=True)
        elif type_ids and min_price and max_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__range=(min_price, max_price), category_id=self.kwargs.get("pk"), visibility=True)
        elif type_ids and min_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__gte=min_price, category_id=self.kwargs.get("pk"), visibility=True)
        elif type_ids and max_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__lte=max_price, category_id=self.kwargs.get("pk"), visibility=True)
        elif min_price and max_price:
            return Product.objects.filter(new_price__range=(min_price, max_price), category_id=self.kwargs.get("pk"), visibility=True)
        elif brand_ids:
            return Product.objects.filter(brand_id__in=brand_ids, category_id=self.kwargs.get("pk"), visibility=True)
        elif type_ids:
            return Product.objects.filter(product_type_id__in=type_ids, category_id=self.kwargs.get("pk"), visibility=True)
        elif min_price:
            return Product.objects.filter(new_price__gte=min_price, category_id=self.kwargs.get("pk"), visibility=True)
        elif max_price:
            return Product.objects.filter(new_price__lte=max_price, category_id=self.kwargs.get("pk"), visibility=True)
        return Product.objects.filter(category_id=self.kwargs.get("pk"), visibility=True)

    def get_context_data(self,**kwargs):
        context = super(CategoryListView,self).get_context_data(**kwargs)
        context['types'] = Type.objects.all()
        context['brands'] = Brand.objects.all()
        return context


class BrandListView(ListView):
    template_name = 'product/product-list.html'
    model = Product
    context_object_name = 'product'
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        types = self.request.GET.getlist('types')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        type_ids = []
        for type_id in types:
            type_ids.append(int(type_id))
        try:
            if min_price.isdigit():
                min_price = int(min_price)
            else:
                min_price = None
        except:
            min_price = None
        try:
            if max_price.isdigit():
                max_price = int(max_price)
            else:
                max_price = None
        except:
            max_price = None

        if type_ids and min_price and max_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__range=(min_price, max_price), brand_id=self.kwargs.get("pk"), visibility=True)
        elif type_ids and min_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__gte=min_price, brand_id=self.kwargs.get("pk"), visibility=True)
        elif type_ids and max_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__lte=max_price, brand_id=self.kwargs.get("pk"), visibility=True)
        elif min_price and max_price:
            return Product.objects.filter(new_price__range=(min_price, max_price), brand_id=self.kwargs.get("pk"), visibility=True)
        elif type_ids:
            return Product.objects.filter(product_type_id__in=type_ids, brand_id=self.kwargs.get("pk"), visibility=True)
        elif min_price:
            return Product.objects.filter(new_price__gte=min_price, brand_id=self.kwargs.get("pk"), visibility=True)
        elif max_price:
            return Product.objects.filter(new_price__lte=max_price, brand_id=self.kwargs.get("pk"), visibility=True)
        return Product.objects.filter(brand_id=self.kwargs.get("pk"), visibility=True)

    def get_context_data(self,**kwargs):
        context = super(BrandListView,self).get_context_data(**kwargs)
        context['types'] = Type.objects.all()
        return context


class TypeListView(ListView):
    template_name = 'product/product-list.html'
    model = Product
    context_object_name = 'product'
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        brands = self.request.GET.getlist('brands')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        brand_ids = []
        for brand_id in brands:
            brand_ids.append(int(brand_id))
        try:
            if min_price.isdigit():
                min_price = int(min_price)
            else:
                min_price = None
        except:
            min_price = None
        try:
            if max_price.isdigit():
                max_price = int(max_price)
            else:
                max_price = None
        except:
            max_price = None

        if brand_ids and min_price and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__range=(min_price, max_price), product_type_id=self.kwargs.get("pk"), visibility=True)
        elif brand_ids and min_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__gte=min_price, product_type_id=self.kwargs.get("pk"), visibility=True)
        elif brand_ids and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__lte=max_price, product_type_id=self.kwargs.get("pk"), visibility=True)
        elif min_price and max_price:
            return Product.objects.filter(new_price__range=(min_price, max_price), product_type_id=self.kwargs.get("pk"), visibility=True)
        elif brand_ids:
            return Product.objects.filter(brand_id__in=brand_ids, product_type_id=self.kwargs.get("pk"), visibility=True)
        elif min_price:
            return Product.objects.filter(new_price__gte=min_price, product_type_id=self.kwargs.get("pk"), visibility=True)
        elif max_price:
            return Product.objects.filter(new_price__lte=max_price, product_type_id=self.kwargs.get("pk"), visibility=True)
        return Product.objects.filter(product_type_id=self.kwargs.get("pk"), visibility=True)

    def get_context_data(self,**kwargs):
        context = super(TypeListView,self).get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        return context


class SuperDealsListView(ListView):
    template_name = 'product/product-list.html'
    model = Product
    context_object_name = 'product'
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        brands = self.request.GET.getlist('brands')
        types = self.request.GET.getlist('types')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        brand_ids = []
        type_ids = []
        for brand_id in brands:
            brand_ids.append(int(brand_id))
        for type_id in types:
            type_ids.append(int(type_id))
        try:
            if min_price.isdigit():
                min_price = int(min_price)
            else:
                min_price = None
        except:
            min_price = None
        try:
            if max_price.isdigit():
                max_price = int(max_price)
            else:
                max_price = None
        except:
            max_price = None

        if brand_ids and type_ids and min_price and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, product_type_id__in=type_ids, new_price__range=(min_price, max_price), super_deals=True, visibility=True)
        elif brand_ids and min_price and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__range=(min_price, max_price), super_deals=True, visibility=True)
        elif brand_ids and type_ids:
            return Product.objects.filter(brand_id__in=brand_ids, product_type_id__in=type_ids, super_deals=True, visibility=True)
        elif brand_ids and min_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__gte=min_price, super_deals=True, visibility=True)
        elif brand_ids and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__lte=max_price, super_deals=True, visibility=True)
        elif type_ids and min_price and max_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__range=(min_price, max_price), super_deals=True, visibility=True)
        elif type_ids and min_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__gte=min_price, super_deals=True, visibility=True)
        elif type_ids and max_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__lte=max_price, super_deals=True, visibility=True)
        elif min_price and max_price:
            return Product.objects.filter(new_price__range=(min_price, max_price), super_deals=True, visibility=True)
        elif brand_ids:
            return Product.objects.filter(brand_id__in=brand_ids, super_deals=True, visibility=True)
        elif type_ids:
            return Product.objects.filter(product_type_id__in=type_ids, super_deals=True, visibility=True)
        elif min_price:
            return Product.objects.filter(new_price__gte=min_price, super_deals=True, visibility=True)
        elif max_price:
            return Product.objects.filter(new_price__lte=max_price, super_deals=True, visibility=True)
        return Product.objects.filter(super_deals=True, visibility=True)

    def get_context_data(self,**kwargs):
        context = super(SuperDealsListView,self).get_context_data(**kwargs)
        context['types'] = Type.objects.all()
        context['brands'] = Brand.objects.all()
        return context


class OfferListView(ListView):
    template_name = 'product/product-list.html'
    model = Product
    context_object_name = 'product'
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        brands = self.request.GET.getlist('brands')
        types = self.request.GET.getlist('types')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        brand_ids = []
        type_ids = []
        for brand_id in brands:
            brand_ids.append(int(brand_id))
        for type_id in types:
            type_ids.append(int(type_id))
        try:
            if min_price.isdigit():
                min_price = int(min_price)
            else:
                min_price = None
        except:
            min_price = None
        try:
            if max_price.isdigit():
                max_price = int(max_price)
            else:
                max_price = None
        except:
            max_price = None

        if brand_ids and type_ids and min_price and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, product_type_id__in=type_ids, new_price__range=(min_price, max_price), offer=True, visibility=True)
        elif brand_ids and min_price and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__range=(min_price, max_price), offer=True, visibility=True)
        elif brand_ids and type_ids:
            return Product.objects.filter(brand_id__in=brand_ids, product_type_id__in=type_ids, offer=True, visibility=True)
        elif brand_ids and min_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__gte=min_price, offer=True, visibility=True)
        elif brand_ids and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__lte=max_price, offer=True, visibility=True)
        elif type_ids and min_price and max_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__range=(min_price, max_price), offer=True, visibility=True)
        elif type_ids and min_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__gte=min_price, offer=True, visibility=True)
        elif type_ids and max_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__lte=max_price, offer=True, visibility=True)
        elif min_price and max_price:
            return Product.objects.filter(new_price__range=(min_price, max_price), offer=True, visibility=True)
        elif brand_ids:
            return Product.objects.filter(brand_id__in=brand_ids, offer=True, visibility=True)
        elif type_ids:
            return Product.objects.filter(product_type_id__in=type_ids, offer=True, visibility=True)
        elif min_price:
            return Product.objects.filter(new_price__gte=min_price, offer=True, visibility=True)
        elif max_price:
            return Product.objects.filter(new_price__lte=max_price, offer=True, visibility=True)
        return Product.objects.filter(offer=True, visibility=True)

    def get_context_data(self,**kwargs):
        context = super(OfferListView,self).get_context_data(**kwargs)
        context['types'] = Type.objects.all()
        context['brands'] = Brand.objects.all()
        return context


class MostViewedListView(ListView):
    template_name = 'product/product-list.html'
    model = Product
    context_object_name = 'product'
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        brands = self.request.GET.getlist('brands')
        types = self.request.GET.getlist('types')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        brand_ids = []
        type_ids = []
        for brand_id in brands:
            brand_ids.append(int(brand_id))
        for type_id in types:
            type_ids.append(int(type_id))
        try:
            if min_price.isdigit():
                min_price = int(min_price)
            else:
                min_price = None
        except:
            min_price = None
        try:
            if max_price.isdigit():
                max_price = int(max_price)
            else:
                max_price = None
        except:
            max_price = None

        if brand_ids and type_ids and min_price and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, product_type_id__in=type_ids, new_price__range=(min_price, max_price), views__gte=10, visibility=True)
        elif brand_ids and min_price and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__range=(min_price, max_price), views__gte=10, visibility=True)
        elif brand_ids and type_ids:
            return Product.objects.filter(brand_id__in=brand_ids, product_type_id__in=type_ids, views__gte=10, visibility=True)
        elif brand_ids and min_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__gte=min_price, views__gte=10, visibility=True)
        elif brand_ids and max_price:
            return Product.objects.filter(brand_id__in=brand_ids, new_price__lte=max_price, views__gte=10, visibility=True)
        elif type_ids and min_price and max_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__range=(min_price, max_price), views__gte=10, visibility=True)
        elif type_ids and min_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__gte=min_price, views__gte=10, visibility=True)
        elif type_ids and max_price:
            return Product.objects.filter(product_type_id__in=type_ids, new_price__lte=max_price, views__gte=10, visibility=True)
        elif min_price and max_price:
            return Product.objects.filter(new_price__range=(min_price, max_price), views__gte=10, visibility=True)
        elif brand_ids:
            return Product.objects.filter(brand_id__in=brand_ids, views__gte=10, visibility=True)
        elif type_ids:
            return Product.objects.filter(product_type_id__in=type_ids, views__gte=10, visibility=True)
        elif min_price:
            return Product.objects.filter(new_price__gte=min_price, views__gte=10, visibility=True)
        elif max_price:
            return Product.objects.filter(new_price__lte=max_price, views__gte=10, visibility=True)
        return Product.objects.filter(views__gte=10, visibility=True)

    def get_context_data(self,**kwargs):
        context = super(MostViewedListView,self).get_context_data(**kwargs)
        context['types'] = Type.objects.all()
        context['brands'] = Brand.objects.all()
        return context


def search_product(request):
    if request.method=='POST':
        search = request.POST.get('srh')

        if search:
            match = Product.objects.filter(Q(name__icontains=search) | Q(product_type__brand_type__icontains=search) | Q(category__name__icontains=search) | Q(brand__name__icontains=search), visibility=True)

            if match:
                return render(request, 'product/product-list.html', {'product':match})
            else:
                messages.error(request, 'no result found')
        else:
            return HttpResponseRedirect('/')

    return render (request, 'product/product-list.html')

def subscription(request):
    if request.method=='POST':
        subscribe = request.POST.get('subs')
        Subscription.objects.get_or_create(email=subscribe)
    return HttpResponseRedirect('/')

class RequestProduct(LoginRequiredMixin, CreateView):
    model = UserRequestProduct
    template_name = 'product/request_product.html'
    form_class = UserRequestProductForm

    def form_valid(self, form):
        product_request = form.save(commit=False)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('product:index')

from django.core.mail import send_mail


class OrderView(LoginRequiredMixin, CreateView):
    template_name = 'product/order.html'
    form_class = UserOrderForm

    def get_context_data(self, *args, **kwargs):
        context = super(OrderView, self).get_context_data(**kwargs)
        context['cart'] = Cart.objects.filter(user_id=self.kwargs.get('pk'), removed=False)
        print(context)
        return context

    def post(self, request, *args, **kwargs):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email', request.user.email)
        contact = request.POST.get('phone', request.user.profile.contact)
        country = request.POST.get('country')
        city = request.POST.get('city')
        street = request.POST.get('street')
        note = request.POST.get('note')
        total_price = request.POST.get('total_price')

        order = UserOrder.objects.create(first_name=first_name, last_name=last_name, email=email, contact=contact, user=request.user,total_price=total_price,country=country,city=city,street=street,note=note)
        c = Cart.objects.filter(user_id=self.request.user.pk, removed=False)
        for item in c:
            order.cart.add(item)

        Cart.objects.filter(user_id=self.request.user.pk).update(removed=True)

        from_email = settings.EMAIL_HOST_USER
        subject = "Order Placed"
        message = "An order has been placed by " + first_name + " " + last_name + ". Contact Details: email= " + email + " contact number= " + contact + " ."
        receipent_email = ['saneprijal@gmail.com', ]
        send_mail(subject, message, from_email, receipent_email)

        return render(request, 'product/success_order.html')


class LaptopPriceListView(ListView):
    template_name = 'product/product-list.html'
    context_object_name = 'product'
    model = Product
    paginate_by = 20

    def get_queryset(self, *args, **kwargs):
        brand_name = self.kwargs.get('brand_name')
        brand_name = brand_name.replace("_", " ")
        return Product.objects.filter(brand__name=self.kwargs.get('brand_name'))


class ContactView(TemplateView):
    template_name = 'product/contact.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        context['about'] = AboutITeam.objects.last()
