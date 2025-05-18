from django.shortcuts import render
from .models import HomeSlider, LookBook
from category.models import Category
from store.models import Product

def home(request):
    # home sliders
    sliders = HomeSlider.objects.filter(is_active=True)
    
    # shopy by category section
    shop_categories = Category.objects.filter(
        main_category__slug='shop',
        image__isnull=False
    ).select_related('main_category').order_by('name_order', 'name')[:6]
    
    # latest arrival product sections by shirt subcategory
    latest_products = Product.objects.filter(
        is_available=True,
        pieces__slug="shirt"
        ).order_by('-created_at')[:12] # limit for homepage
    
    # Lookbook section 
    lookbooks = LookBook.objects.filter(is_active=True).order_by('order', '-created_at')
    
    
    context = {
        'sliders': sliders,
        'shop_categories': shop_categories,
        'latest_products': latest_products,
        'lookbooks': lookbooks,
    }
    
    
    return render(request, 'home.html', context)
