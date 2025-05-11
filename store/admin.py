from django.contrib import admin
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase
from django.utils.html import format_html
from easy_thumbnails.files import get_thumbnailer
from store.models import (
    Product, Style,
    FabricCategory, Color,
    Season, Pattern, Material, ProductImage, ProductGroup
)

class ProductImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_thumbnail', 'image', 'alt_text', 'order')
    ordering = ['order']
    readonly_fields = ('image_thumbnail',)
    show_change_link = True
    
    def image_thumbnail(self, obj):
        if obj.image:
            thumbnail_options = {'size': (80, 80), 'crop': True}
            thumb_url = get_thumbnailer(obj.image).get_thumbnail(thumbnail_options).url
            return format_html('<img src="{}" width="80" height="80" />', thumb_url)
        return "-"
    image_thumbnail.short_description = "Thumbnail"
    

@admin.register(Product)
class ProductAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ['name', 'group', 'sub_category', 'price', 'is_available', 'first_image_preview']
    list_filter = ['is_available', 'group', 'sub_category', 'style']
    search_fields = ['name', 'description', 'group__name']
    list_editable = ['price', 'is_available']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    show_facets = admin.ShowFacets.ALWAYS
    
    def first_image_preview(self, obj):
        first_image = obj.images.order_by('order').first()
        if first_image and first_image.image:
            thumb_url = get_thumbnailer(first_image.image).get_thumbnail({'size': (50, 50), 'crop': True}).url
            return format_html('<img src="{}" width="50" height="50" />', thumb_url)
        return "-"
    
    first_image_preview.short_description = "Preview"
    
    
    

@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(FabricCategory)
class FabricCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    
@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['name']
    
@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    list_display = ['name']
    
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code']


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}


