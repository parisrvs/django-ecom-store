from django.contrib import admin
from . import models
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from datetime import datetime, timezone


class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "is_staff", "orders_count"]

    @admin.display(ordering="orders_count")
    def orders_count(self, user):
        url = reverse("admin:store_order_changelist") + '?' + urlencode({
            "customer__id": str(user.id)
        })
        return format_html("<a href='{}'>{}</a>", url, user.orders_count) 
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count("orders")
        )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


### Orders
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    actions = ["mark_closed", "cancel_order", "process_cancellation"]
    list_display = ["id", "customer", "amount_payable", "order_status", "items_count", "placed_at", "expected_delivery_time"]
    list_select_related = ["discount", "cancellation", "customer"]
    search_fields = ["id"]
    list_filter = ["placed_at", "order_status"]
    list_per_page = 20


    @admin.display(ordering="items_count")
    def items_count(self, order):
        url = reverse("admin:store_orderitem_changelist") + '?' + urlencode({
            "order__id": str(order.id)
        })
        return format_html("<a href='{}'>{}</a>", url, order.items_count) 
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            items_count=Count("orderitems")
        )
    
    @admin.action(description="Mark as Closed")
    def mark_closed(self, request, queryset):
        updated_count = 0
        for order in queryset:
            if order.order_status == 'O':
                order.order_status = 'C'
                order.payment_status = 'S'
                order.closed_at = datetime.now(timezone.utc)
                order.save()
                updated_count += 1
        self.message_user(
            request,
            f"{updated_count} orders were successfully closed."
        )
    

    @admin.action(description="Cancel Order")
    def cancel_order(self, request, queryset):
        updated_count = 0
        for order in queryset:
            if order.order_status == 'P':
                order.order_status = 'N'
                order.payment_status = 'U'
                order.cancelled_at = datetime.now(timezone.utc)
                order.save()
                updated_count += 1

                for item in order.orderitems.select_related("product").all():
                    item.product.inventory += item.quantity
                    if item.product.inventory > 0:
                        item.product.availability = True
                    item.product.save()
        self.message_user(
            request,
            f"{updated_count} orders were successfully cancelled."
        )


    @admin.action(description="Process Cancellation")
    def process_cancellation(self, request, queryset):
        updated_count = 0
        for order in queryset:
            if order.order_status == 'O':
                order.order_status = 'P'
                order.payment_status = 'U'
                order.save()
            
                oc = models.OrderCancellation.objects.create(
                    order = order
                )
                updated_count += 1
        self.message_user(
            request,
            f"Processing cancellation for {updated_count} orders."
        )



### Order Items
@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "order_customer", "product", "quantity", "amount_payable"]
    list_select_related = ["order", "order__customer", "product", "product__product"]
    readonly_fields = ["order", "product", "discount_percent"]
    search_fields = ["order__id"]
    list_per_page = 20
    
    def order_customer(self, orderitem):
        return orderitem.order.customer


### Cancelled Orders
@admin.register(models.OrderCancellation)
class OrderCancellationAdmin(admin.ModelAdmin):
    list_display = ["order", "cancelled_at", "order_customer"]
    readonly_fields = ["order"]
    search_fields = ["order__id"]
    list_per_page = 20
    
    def order_customer(self, cancelleditem):
        return cancelleditem.order.customer


### Address
@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_filter = ["user", "city", "state", "country"]
    list_display = ["user", "address1", "city", "pincode", "mobile"]
    empty_value_display = '-empty-'
    search_fields = ["address1", "address2", "landmark"]
    list_per_page = 20


########## Image ##########
@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['image', 'name']
    list_editable = ['name']
    list_per_page = 10
    search_fields = ['name']


### Product Tags
@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']
    ordering = ['name']
    search_fields = ['name']
    list_per_page = 20


### Category
@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'product_count']
    list_per_page = 10
    ordering = ['title']
    search_fields = ['title']
    prepopulated_fields = {
        'slug': ['title']
    }

    @admin.display(ordering='product_count')
    def product_count(self, category):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'categories__id': str(category.id)
            })
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            category.product_count
        )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('products')
        )


### Pincode
@admin.register(models.Pincode)
class PincodeAdmin(admin.ModelAdmin):
    list_display = ["pincode", "delivery_time_in_days"]
    list_editable = ["delivery_time_in_days"]
    autocomplete_fields = ["products_unavailable"]
    list_per_page = 10
    search_fields = ["pincode__startswith"]


### Product
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'variation_count']
    list_per_page = 10
    list_filter = ['categories__title']
    search_fields = ['title__istartswith']
    filter_horizontal = ["tags", "categories"]
    prepopulated_fields = {
        'slug': ['title']
    }

    @admin.display(ordering='variation_count')
    def variation_count(self, product):
        url = (
            reverse('admin:store_variation_changelist')
            + '?'
            + urlencode({
                'product__id': str(product.id)
            })
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            product.variation_count
        )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            "categories", "tags"
        ).annotate(
            variation_count=Count('variations')
        )


### Inventory Filter for Variations
class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', "Low")
        ]
    
    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


### Variation
@admin.register(models.Variation)
class VariationAdmin(admin.ModelAdmin):
    autocomplete_fields = ['product']
    list_display = ['product', 'price', 'unit', 'availability', 'inventory', 'inventory_status', 'orders_count']
    list_editable = ['price', 'availability', 'inventory']
    list_per_page = 10
    list_filter = [InventoryFilter, 'keyvalues__value']
    search_fields = ['product__title__istartswith']
    filter_horizontal = ["images", "keyvalues"]
    list_select_related = [models.Product, models.Variation.keyvalues, models.Variation.images, models.KeyValue.key, models.KeyValue.value]
    
    @admin.display(ordering='inventory')
    def inventory_status(self, variation):
        if variation.inventory < 10:
            return 'Low'
        return 'OK'
    
    @admin.display(ordering="orders_count")
    def orders_count(self, variation):
        return variation.orders_count
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product").annotate(
            orders_count=Count("orderitems")
        )


### Discount
@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    actions = ['clear_discounts']
    list_display = ['id', 'code', 'percent']
    list_editable = ['code', 'percent']
    search_fields = ["percent"]
    list_per_page = 20

    @admin.action(description='Clear Discounts')
    def clear_discounts(self, request, queryset):
        updated_count = queryset.update(percent=0)
        self.message_user(
            request,
            f'{updated_count} discounts were successfully updated.'
        )


### Keys
@admin.register(models.Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_count']
    search_fields = ['key']

    @admin.display(ordering='value_count')
    def value_count(self, key):
        url = (
            reverse('admin:store_value_changelist')
            + '?'
            + urlencode({
                'key__id': str(key.id)
            })
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            key.value_count
        )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            value_count=Count('values')
        )


### Value
@admin.register(models.Value)
class ValueAdmin(admin.ModelAdmin):
    search_fields = ['value']


### Key - Values
@admin.register(models.KeyValue)
class KeyValueAdmin(admin.ModelAdmin):
    autocomplete_fields = ['key', 'value']
    list_display = ['id', 'key_title', 'value_title', 'product_count']
    list_select_related = ['key', 'value']
    search_fields = ['key__key__istartswith', 'value__value__istartswith']

    @admin.display(ordering='key')
    def key_title(self, keyvalue):
        return keyvalue.key.key
    
    @admin.display(ordering='value')
    def value_title(self, keyvalue):
        return keyvalue.value.value
    
    @admin.display(ordering='product_count')
    def product_count(self, keyvalue):
        url = (
            reverse('admin:store_variation_changelist')
            + '?'
            + urlencode({
                'keyvalues__id': str(keyvalue.id)
            })
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            keyvalue.product_count
        )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('variation')
        )
