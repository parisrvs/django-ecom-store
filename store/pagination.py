from django.core.paginator import Paginator
from .models import Product, Category, Tag


def get_products(request, category_slug):
    if category_slug:
        try:
            c = Category.objects.get(slug=category_slug)
        except:
            return None
        else:
            products = c.products.prefetch_related("images", "variations").all()
    else:
        products = Product.objects.prefetch_related("images", "variations").all()
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


def get_orders(request):
    orders = request.user.person.orders.select_related("address", "cancellation", "discount").all()
    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


def get_search_products(request, q):
    products = Product.objects.prefetch_related("images", "variations").filter(title__istartswith=q)
    tags = Tag.objects.prefetch_related("products").filter(name__istartswith=q)
    for tag in tags:
        products = products.union(tag.products.prefetch_related("images", "variations").all()).order_by('title')
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj