from django.shortcuts import get_object_or_404, render
from cart.forms import CartAddProductForm
from category.models import MainCategory, Category, SubCategory
from store.models import Product, ProductImage
from django.db.models import Count, Q
from django.utils import timezone
from collections import defaultdict


def store(request, main_slug=None, category_slug=None, subcategory_slug=None):
    main_category = None
    category = None
    sub_category = None
    subcategories = None
    products = Product.objects.filter(is_available=True)
    
    active_main_category_id = None 
    
    if main_slug and category_slug and subcategory_slug:
        # Filter by subcategory
        sub_category = get_object_or_404(SubCategory, 
                    slug=subcategory_slug, 
                    category__slug=category_slug, 
                    category__main_category__slug=main_slug
        )
        category = sub_category.category
        products = products.filter(sub_category=sub_category)
        active_main_category_id = sub_category.category.main_category.id
        
    elif main_slug and category_slug:
        # Filter by category
        category = get_object_or_404(Category, slug=category_slug, main_category__slug=main_slug)
        subcategories = category.subcategories.annotate(
            product_count = Count('products', filter=Q(products__is_available=True))
        )
        products = products.filter(sub_category__in=subcategories)
        active_main_category_id = category.main_category.id
        
    elif main_slug:
        # Filter by MainCategory
        main_category = get_object_or_404(MainCategory, slug=main_slug)
        categories = main_category.categories.all()
        subcategories = SubCategory.objects.filter(category__in=categories).annotate(
            product_count = Count('products', filter=Q(products__is_available=True))
        )
        products = products.filter(sub_category__in=subcategories)
        active_main_category_id = main_category.id
    
    context = {
        'main_category': main_category,
        'category': category,
        'sub_category': sub_category,
        'subcategories': subcategories, 
        'products': products,
        'active_category_id': category.id if category else None,
        'active_main_category_id': active_main_category_id,
    }
    
    
    return render(request, 'store/store.html', context)


def product_detail(request, main_slug, category_slug, subcategory_slug, product_slug):
    product = get_object_or_404(
        Product,
        slug=product_slug,
        sub_category__slug=subcategory_slug,
        sub_category__category__slug=category_slug,
        sub_category__category__main_category__slug=main_slug
    )
    
    cart_product_form = CartAddProductForm()
    
    # Fetch images for this single product only
    images = ProductImage.objects.filter(
        product=product
    ).select_related('color').order_by('order')
    
    # Countdown logic
    timer = 0
    if product.countdown_end:
        remaining = (product.countdown_end - timezone.now()).total_seconds()
        timer = max(int(remaining), 0)

    context = {
        'product': product,
        'images': images,
        'first_image': product.first_image(),
        'timer': timer,
        'cart_product_form': cart_product_form,
    }
    return render(request, 'store/product_detail.html', context)