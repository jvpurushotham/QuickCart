from .models import Cart, Wishlist

# Cart count
def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user = request.user)
            count = cart.item_count
        except Cart.DoesNotExist:
            pass
    return {'cart_count': count}

# Wishlist count
def wishlist_count(request):
    count = 0
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user = request.user).count()
    return {'wishlist_count': count}





