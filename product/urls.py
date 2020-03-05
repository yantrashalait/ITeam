from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('', views.index, name='index'),

    # crud for products
    path('product/list/', views.ProductList.as_view(), name='product-list'),
    path('product/detail/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('product/list/category/<int:pk>', views.CategoryListView.as_view(), name='product-category-list'),
    path('product/list/brand/<int:pk>/', views.BrandListView.as_view(), name='product-brand-list'),
    path('product/list/type/<int:pk>/', views.TypeListView.as_view(), name='product-type-list'),
    path('product/list/super-deals/', views.SuperDealsListView.as_view(), name='product-super-deals-list'),
    path('product/list/offer/', views.OfferListView.as_view(), name='product-offer-list'),
    path('product/list/most-viewed/', views.MostViewedListView.as_view(), name='product-most-viewed-list'),
    path('search/', views.search_product, name='search-product'),

    # view all notifications of user
    path('notifications/<int:pk>/', views.NotificationListView.as_view(), name='notification'),
    # view all waitlists of user
    path('waitlist/<int:pk>/', views.WaitListView.as_view(), name='waitlist'),
    path('waitlist/add', views.add_to_waitlist, name='waitlist-add'),

    path('bargain/add', views.add_to_bargain, name='bargain-add'),

    # view all cart of user
    path('cart/<int:pk>/', views.CartListView.as_view(), name='cart-list'),
    path('cart/add/', views.AddCart.as_view(), name='add-cart'),

    # view all favourites of user
    path('favourite/<int:pk>/', views.FavouriteListView.as_view(), name='favourite'),

    # mark a notification as seen
    path('notification/view/<int:pk>/', views.see_notification, name='see-notification'),

    # add to favourite
    path('favourite/add/', views.add_to_favourite, name='add_favourite'),

    # subscription
    path('subscription/', views.subscription, name='subscribe'),

    path('request/', views.RequestProduct.as_view(), name='request-product'),
    path('order/<int:pk>', views.OrderView.as_view(), name='order'),

    # prices in nepal urls
    path('laptop/price/nepal/laptop_prices_in_nepal/<slug:brand_name>', views.LaptopPriceListView.as_view(), name='laptop-price-in-nepal'),

    path('contact', views.ContactView.as_view(), name="contact"),

]
