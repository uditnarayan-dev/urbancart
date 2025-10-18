from .models import Cart, Category

def cart_item_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        count = 0
        for item in cart:
            count += item.quantity
    else:
        count = 0
    return {'cart_item_count': count}

def active_categories(request):
    categories = Category.objects.filter(is_active=True)
    return {'active_categories': categories}