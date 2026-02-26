from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from decimal import Decimal
import json

# Importing the odels 
from .models import (Category, Product, Cart, CartItem, Wishlist,
                     Order, OrderItem, Address, Coupon, Review)

# Importing the forms 
from .forms import RegisterForm, AddressForm, ReviewForm

# Home 
def home(request):
    categories = Category.objects.all()
    best_sellers = Product.objects.filter(is_active = True).order_by('-id')[:8]
    recent_products = Product.objects.filter(is_active = True).order_by('-created_at')[:8]
    offers = Product.objects.filter(is_active=True, discount__gt = 0).order_by('-discount')[:8]
    
    context = {
        'categories': categories,
        'best_sellers': best_sellers,
        'recent_products': recent_products,
        'offers': offers,
    }

    return render(request, 'store/home.html', context)

# Product list
def product_list(request, slug = None):
    products = Product.objects.filter(is_active = True).select_related('category')
    category = None

    if slug:
        category = get_object_or_404(Category, slug = slug)
        products = products.filter(category = category)

    query = request.GET.get('q', '')
    if query:
        products = products.filter(Q(name__icontains = query) | Q(description__icontains = query))
    
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    products = paginator.get_page(page)

    return render(request, 'store/product_list.html', {
        'products': products,
        'category': category,
        'categories': Category.objects.all(),
        'query': query,
    })

# Product details
def product_detail(request, pk):
    product = get_object_or_404(Product, pk = pk, is_active = True)
    reviews = product.reviews.select_related('user').all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    related = Product.objects.filter(category = product.category, is_active = True).exclude(pk = pk)[:4]
    in_wishlist = False
    
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user = request.user, product = product).exists()
    
    review_form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)

        if review_form.is_valid():
            rev, created = Review.objects.update_or_create(
                user = request.user, product = product,

                defaults={'rating': review_form.cleaned_data['rating'],
                          'comment': review_form.cleaned_data['comment']}
            )
            messages.success(request, 'Review submitted!')
            
            return redirect('product_detail', pk = pk)
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related': related,
        'in_wishlist': in_wishlist,
        'review_form': review_form,
    })

# Searching 
def search(request):
    query = request.GET.get('q', '')

    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    ) if query else Product.objects.none()

    return render(request, 'store/product_list.html', {
        'products': products,
        'query': query,
        'categories': Category.objects.all(),
    })


# Auth 
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome to QuickCart, {user.username}!')
        return redirect('home')
    
    return render(request, 'registration/register.html', {'form': form})

# Login view 
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect(request.GET.get('next', 'home'))
    
    return render(request, 'registration/login.html', {'form': form})

# Logout view 
def logout_view(request):
    logout(request)
    return redirect('home')

# Profile 
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'store/profile.html', {'orders': orders, 'addresses': addresses})


# Cart 
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user = request.user)
    items = cart.items.select_related('product').all()
    return render(request, 'store/cart.html', {'cart': cart, 'items': items})

# Add to cart 
@login_required
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status = 405)
    
    product = get_object_or_404(Product, pk = product_id, is_active = True)
    cart, _ = Cart.objects.get_or_create(user = request.user)
    item, created = CartItem.objects.get_or_create(cart = cart, product = product)

    if not created:
        item.quantity += 1
        item.save()

    return JsonResponse({
        'success': True,
        'quantity': item.quantity,
        'cart_count': cart.item_count,
        'message': f'{product.name} added to cart!'
    })

# Update cart 
@login_required
def update_cart(request, item_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status = 405)
    
    item = get_object_or_404(CartItem, pk = item_id, cart__user = request.user)
    data = json.loads(request.body)
    action = data.get('action')

    if action == 'increment':
        item.quantity += 1
        item.save()
    elif action == 'decrement':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
            cart = Cart.objects.get(user=request.user)

            return JsonResponse({'success': True, 'removed': True,
                                 'cart_total': float(cart.total),
                                 'cart_count': cart.item_count})
        
    cart = Cart.objects.get(user=request.user)
    return JsonResponse({
        'success': True,
        'quantity': item.quantity,
        'subtotal': float(item.subtotal),
        'cart_total': float(cart.total),
        'cart_count': cart.item_count,
    })

# Remove product from cart
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user = request.user)
    item.delete()
    cart = Cart.objects.get(user=request.user)
    return JsonResponse({'success': True, 'cart_total': float(cart.total),
                         'cart_count': cart.item_count})


# Wishlist 
@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user = request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'items': items})

# Toggling Wishlist 
@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk = product_id)
    obj, created = Wishlist.objects.get_or_create(user = request.user, product = product)

    if not created:
        obj.delete()
        return JsonResponse({'success': True, 'in_wishlist': False, 'message': 'Removed from wishlist'})
    return JsonResponse({'success': True, 'in_wishlist': True, 'message': 'Added to wishlist!'})


# Checkout & Orders 
@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()

    if not items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')
    
    addresses = Address.objects.filter(user=request.user)
    address_form = AddressForm()
    coupon_code = ''
    discount = Decimal('0')

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        coupon_code = request.POST.get('coupon', '').strip().upper()

        if address_id:
            address = get_object_or_404(Address, pk=address_id, user=request.user)
        else:
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user
                address.save()
            else:
                return render(request, 'store/checkout.html', {
                    'cart': cart, 'items': items, 'addresses': addresses,
                    'address_form': address_form
                })

        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                if cart.total >= coupon.min_order_amount:
                    discount = cart.total * coupon.discount_percent / 100
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid coupon code.')

        final_total = cart.total - discount
        order = Order.objects.create(
            user=request.user, address=address,
            total_price=final_total, coupon=coupon,
            discount_amount=discount
        )

        for item in items:
            OrderItem.objects.create(
                order=order, product=item.product,
                quantity=item.quantity, price=item.product.discounted_price
            )

            # reduce stock
            item.product.stock = max(0, item.product.stock - item.quantity)
            item.product.save()

        cart.items.all().delete()
        messages.success(request, f'Order #{order.id} placed successfully! Estimated delivery: {order.estimated_delivery}')
        
        return redirect('order_detail', pk=order.id)

    return render(request, 'store/checkout.html', {
        'cart': cart, 'items': items, 'addresses': addresses,
        'address_form': address_form,
    })

# Order list 
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_list.html', {'orders': orders})

# Order details 
@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})

# Applying coupons 
@login_required
def apply_coupon(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    code = data.get('code', '').strip().upper()
    cart, _ = Cart.objects.get_or_create(user=request.user)

    try:
        coupon = Coupon.objects.get(code=code, active=True)
        if cart.total < coupon.min_order_amount:
            return JsonResponse({'success': False,
                                 'message': f'Minimum order ₹{coupon.min_order_amount} required'})
        
        discount = float(cart.total * coupon.discount_percent / 100)
        
        return JsonResponse({'success': True, 'discount': discount,
                             'final_total': float(cart.total) - discount,
                             'message': f'{coupon.discount_percent}% off applied!'})
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid coupon code'})

# Add address 
@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            addr.save()
            messages.success(request, 'Address added!')

    return redirect('profile')
