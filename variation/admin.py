from django.contrib import admin
from .models import VariationType, VariationOption

@admin.register(VariationType)
class VariationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    
@admin.register(VariationOption)
class VariationOptionAdmin(admin.ModelAdmin):
    list_display = ['type', 'name', 'order']
    list_filter = ['type']
    search_fields = ['name']
