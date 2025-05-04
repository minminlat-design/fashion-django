from django.db import models
from django.urls import reverse
from category.models import SubCategory
from django.forms import ValidationError

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products') # must not use '' cos it is imported from another app
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    style = models.ForeignKey('Style', on_delete=models.SET_NULL, null=True, blank=True)  # For suit, jacket, pants styles
    color = models.ForeignKey('Color', on_delete=models.SET_NULL, null=True, blank=True)  # Default/primary color
    material = models.ForeignKey('Material', on_delete=models.SET_NULL, null=True, blank=True)
    pattern = models.ForeignKey('Pattern', on_delete=models.SET_NULL, null=True, blank=True)
    season = models.ForeignKey('Season', on_delete=models.SET_NULL, null=True, blank=True)
    occasion = models.ForeignKey('FabricCategory', on_delete=models.SET_NULL, null=True, blank=True)
    is_customizable = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]
        
    
    def clean(self):
        if self.discounted_price and self.discounted_price >= self.price:
            raise ValidationError("Discounted price must be less than original price.")


    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse(
            'store:product_detail',
            args=[
                self.sub_category.category.main_category.slug,
                self.sub_category.category.slug,
                self.sub_category.slug,
                self.slug
            ]
        )

    

class Style(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., Slim Fit, Classic Fit
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    

    
class Season(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g. All-Season, Summer, Winter
    
    def __str__(self):
        return self.name
    
class Pattern(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., Plain, Stripe, Check
    
    def __str__(self):
        return self.name
    
class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g. Wool, linen
    
    def __str__(self):
        return self.name
    
class FabricCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., Business, Wedding
    
    class Meta:
        verbose_name_plural = "Fabric Categories"
    
    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., Navy Blue
    hex_code = models.CharField(max_length=7, blank=True, null=True)  # e.g., #000080 for frontend use
    image = models.ImageField(upload_to='colors/', blank=True, null=True)  # optional swatch

    def __str__(self):
        return self.name



