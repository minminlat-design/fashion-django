from django.contrib import admin
from .models import MainCategory, Category, SubCategory

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
    ordering = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['main_category', 'image', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
    ordering = ['main_category', 'name']
    
    

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['category', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
    ordering = ['category', 'name']
    

