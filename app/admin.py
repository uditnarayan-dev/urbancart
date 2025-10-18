from django.contrib import admin
from .models import Customer, Product, OrderPlaced, Cart, Category, Brand, ProductImage, Banner, Sale


# ----------------------------
# Customer
# ----------------------------
@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'locality', 'city', 'zipcode', 'state']
    search_fields = ['name', 'city', 'state']


# ----------------------------
# Category
# ----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']
    search_fields = ['name']


# ----------------------------
# Brand
# ----------------------------
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']
    search_fields = ['name']


# ----------------------------
# Product
# ----------------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # number of extra forms to display

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = [
        'id', 'title', 'brand_fk', 'category_fk',
        'selling_price', 'discounted_price'
    ]
    list_filter = ['brand_fk', 'category_fk']
    search_fields = ['title', 'brand_fk__name', 'category_fk__name']
    autocomplete_fields = ['brand_fk', 'category_fk']


# ----------------------------
# Cart
# ----------------------------
@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity']
    list_filter = ['user']
    search_fields = ['user__username', 'product__title']


# ----------------------------
# OrderPlaced
# ----------------------------
@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'customer', 'product', 'quantity',
        'ordered_date', 'status', 'payment_method'
    ]
    list_filter = ['status', 'payment_method']
    search_fields = ['user__username', 'customer__name', 'product__title']

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_active', 'display_order']
    list_editable = ['is_active', 'display_order']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'start_date', 'end_date', 'is_active']
    list_editable = ['is_active']
    list_filter = ['is_active', 'start_date', 'end_date']