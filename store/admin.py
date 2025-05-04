from django.contrib import admin
from store.models import (
    Product, Style,
    FabricCategory, Color,
    Season, Pattern, Material
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sub_category', 'price', 'image', 'is_available']
    list_filter = ['is_available', 'sub_category', 'style']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_available']
    prepopulated_fields = {'slug': ('name',)}
    show_facets = admin.ShowFacets.ALWAYS
    
    

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



