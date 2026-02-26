from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('products/', views.product_list, name = 'product_list'),
    path('products/category/<slug:slug>/', views.product_list, name = 'category_products'),
    path('products/<int:pk>/', views.product_detail, name = 'product_detail'),
    path('search/', views.search, name = 'search'),

    # Auth
    path('register/', views.register_view, name = 'register'),
    path('login/', views.login_view, name = 'login'),
    path('logout/', views.logout_view, name = 'logout'),
    path('profile/', views.profile, name = 'profile'),

    # Cart
    path('cart/', views.cart_view, name = 'cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name = 'add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name = 'update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name = 'remove_from_cart'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name = 'wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name = 'toggle_wishlist'),

    # Checkout & Orders
    path('checkout/', views.checkout, name = 'checkout'),
    path('checkout/apply-coupon/', views.apply_coupon, name = 'apply_coupon'),
    path('orders/', views.order_list, name = 'order_list'),
    path('orders/<int:pk>/', views.order_detail, name = 'order_detail'),
    path('address/add/', views.add_address, name = 'add_address'),
]





