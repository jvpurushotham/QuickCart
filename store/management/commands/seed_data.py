from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product, Coupon


class Command(BaseCommand):
    help = 'Seed QuickCart with demo categories, products, coupons, and a superuser'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding QuickCart demo data...\n')

        # Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@quickcart.com', 'admin123')
            self.stdout.write('✅ Superuser created: admin / admin123')

        # Categories
        cats = [
            ('Fruits & Vegetables', 'fruits-vegetables'),
            ('Dairy & Eggs', 'dairy-eggs'),
            ('Snacks', 'snacks'),
            ('Beverages', 'beverages'),
            ('Bakery', 'bakery'),
            ('Meat & Seafood', 'meat-seafood'),
            ('Personal Care', 'personal-care'),
            ('Household', 'household'),
        ]
        cat_objs = {}
        for name, slug in cats:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            cat_objs[slug] = cat
        self.stdout.write(f'✅ {len(cats)} categories created')

        # Products
        products = [
            # Fruits & Veg
            ('Fresh Bananas (6 pcs)', 'fruits-vegetables', 45, 'Sweet & ripe bananas', 100, 10),
            ('Red Apples (1 kg)', 'fruits-vegetables', 120, 'Crisp & juicy apples', 80, 15),
            ('Baby Spinach (200g)', 'fruits-vegetables', 35, 'Tender baby spinach leaves', 60, 0),
            ('Tomatoes (500g)', 'fruits-vegetables', 30, 'Fresh vine tomatoes', 90, 0),
            # Dairy
            ('Full Cream Milk (1L)', 'dairy-eggs', 68, 'Farm-fresh full cream milk', 150, 0),
            ('Amul Butter (500g)', 'dairy-eggs', 245, 'Pasteurized table butter', 50, 5),
            ('Greek Yogurt (400g)', 'dairy-eggs', 89, 'Thick and creamy yogurt', 75, 10),
            ('Eggs (12 pcs)', 'dairy-eggs', 99, 'Farm fresh eggs', 200, 0),
            # Snacks
            ('Lays Classic (90g)', 'snacks', 30, 'Classic salted chips', 200, 0),
            ('Biscoff Cookies (250g)', 'snacks', 195, 'Caramelised biscuits', 40, 0),
            ('Mixed Nuts (200g)', 'snacks', 320, 'Cashews, almonds & walnuts', 30, 20),
            # Beverages
            ('Tropicana Orange (1L)', 'beverages', 99, '100% real fruit juice', 80, 10),
            ('Red Bull (250ml)', 'beverages', 125, 'Energy drink', 120, 0),
            ('Green Tea (25 bags)', 'beverages', 110, 'Premium green tea', 60, 0),
            # Bakery
            ('Whole Wheat Bread', 'bakery', 55, 'Freshly baked whole wheat', 40, 0),
            ('Croissants (4 pcs)', 'bakery', 120, 'Buttery flaky croissants', 25, 15),
        ]

        count = 0
        for name, cat_slug, price, desc, stock, discount in products:
            Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat_objs[cat_slug],
                    'price': price,
                    'description': desc,
                    'stock': stock,
                    'discount': discount,
                    'is_active': True,
                }
            )
            count += 1
        self.stdout.write(f'✅ {count} products created')

        # Coupons
        Coupon.objects.get_or_create(code='WELCOME20', defaults={'discount_percent': 20, 'active': True, 'min_order_amount': 100})
        Coupon.objects.get_or_create(code='SAVE50', defaults={'discount_percent': 10, 'active': True, 'min_order_amount': 500})
        self.stdout.write('✅ Coupons created: WELCOME20, SAVE50')

        self.stdout.write('\n🎉 QuickCart demo data seeded successfully!')
        self.stdout.write('   Admin: http://localhost:8000/admin/ (admin / admin123)')
        self.stdout.write('   App:   http://localhost:8000/')
