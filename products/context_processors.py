from .models import NewProduct

def new_products(request):
    """Context processor to make new products available in all templates"""
    return {
        'new_products': NewProduct.objects.filter(is_active=True).order_by('display_order', '-created_at')
    }






