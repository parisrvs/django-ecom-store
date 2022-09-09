from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("database/", views.database_update, name="database_update"),
    path("database/clear/", views.clear_database_but_images, name="clear_database_but_images"),
    path("database/clear/images/", views.clear_database_images, name="clear_database_images"),

    path('', views.homepage, name="homepage"),
    path('search/', views.search, name="search"),
    path("apply-discount/", views.apply_discount),
    path("products/get-variations/", views.get_variations, name="get_variations"),
    path("products/add-to-cart/", views.add2cart, name="add2cart"),
    path("products/<slug:product_slug>/", views.product, name="product"),
    path("products/<slug:product_slug>/<int:variation_id>/", views.variation, name="variation"),
    path("cart/", views.getCart),
    path("cart/add-delivery-address/", views.addDeliveryAddress2Cart),
    path("cart/add-new-delivery-address/", views.addNewDeliveryAddress2Cart),
    path("cart/remove-delivery-address/", views.removeSelectedDeliveryAddress2Cart),
    path("cart/clear/", views.clearCart),
    path("cart/remove-item/", views.removeFromCart),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/place-order/", views.place_order),
    path('get-user-address/', views.getUserAddress),
    path('orders/', views.orders, name="orders"),
    path('orders/cancel/', views.cancelOrder),
    path('orders/re-open/<int:order_id>/', views.reopenOrder, name="reopenOrder"),
    path('orders/<int:order_id>/', views.order, name="order"),
    path("<slug:category_slug>/", views.homepage, name="products_by_category"),
]
