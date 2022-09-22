from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('search/', views.search, name='search'),
    path('apply-discount/', views.apply_discount),
    path('add-to-cart/', views.add2cart),
    path('remove-from-cart/', views.removeFromCart),
    path('get-cart/', views.getCart),
    path('clear-cart/', views.clearCart),
    path('get-products/', views.getProducts),
    path('check-deliverability/', views.checkDeliverability),

    path('checkout/', views.checkout, name="checkout"),
    path('checkout/select-delivery-address/', views.selectDeliveryAddress),
    path('checkout/remove-selected-delivery-address/', views.removeSelectedDeliveryAddress),
    path('checkout/get-delivery-address/', views.getDeliveryAddress),
    path('checkout/place-order/', views.placeOrder),

    path('orders/', views.orders, name="orders"),
    path('orders/cancel/', views.cancelOrder),
    path('orders/<int:order_id>/', views.order, name="order"),
    
    path('profile/', views.profile, name='profile'),
    path('profile/get-user/', views.getUser),
    path('profile/add-address/', views.addAddress),
    path('profile/make-address-primary/', views.makeAddressPrimary),
    path('profile/delete-address/', views.deleteAddress),
    path('profile/get-address/', views.getAddress),
    path('profile/edit-address/', views.editAddress),

    path('<str:product_slug>/', views.products, name='products'),
    path('<str:product_slug>/<int:variation_id>/', views.product, name='product')
]