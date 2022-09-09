from django.contrib import admin
from . import models
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass

@admin.register(models.OrderCancellation)
class OrderCancellationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['image', 'name']
    list_editable = ['name']
    list_per_page = 10
    search_fields = ['name']


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']
    ordering = ['name']
    search_fields = ['name']


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


class ProductVariationInline(admin.StackedInline):
    model = models.Variation
    min_num = 1
    extra = 0
    autocomplete_fields = ['product', 'images', 'keyvalues']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['images', 'tags', 'categories']
    inlines = [ProductVariationInline]
    list_display = ['title']
    list_per_page = 10
    list_filter = ['categories__title']
    search_fields = ['title__istartswith']
    prepopulated_fields = {
        'slug': ['title']
    }


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


@admin.register(models.Value)
class ValueAdmin(admin.ModelAdmin):
    search_fields = ['value']


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


@admin.register(models.Variation)
class VariationAdmin(admin.ModelAdmin):
    autocomplete_fields = ['product', 'images', 'keyvalues']
    list_display = ['product', 'price', 'unit', 'availability', 'inventory', 'inventory_status']
    list_editable = ['price', 'availability', 'inventory']
    list_per_page = 10
    list_filter = [InventoryFilter, 'keyvalues__value']
    search_fields = ['product__title__istartswith']

    @admin.display(ordering='inventory')
    def inventory_status(self, variation):
        if variation.inventory < 10:
            return 'Low'
        return 'OK'


@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    actions = ['clear_discounts']
    list_display = ['id', 'code', 'percent']
    list_editable = ['code', 'percent']

    @admin.action(description='Clead Discounts')
    def clear_discounts(self, request, queryset):
        updated_count = queryset.update(percent=0)
        self.message_user(
            request,
            f'{updated_count} discounts were successfully updated.'
        )


@admin.register(models.KeyValue)
class KeyValueAdmin(admin.ModelAdmin):
    autocomplete_fields = ['key', 'value']
    list_display = ['id', 'key_title', 'value_title', 'product_count']
    # list_editable = ['key_title', 'value_title']
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