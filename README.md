# ⚡ QuickCart – Instant Grocery Delivery Web App

A full-stack, Blinkit-inspired grocery delivery web application built with **Django + Vanilla JS**.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
cd quickcart
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py migrate
```

### 3. Seed demo data (categories, products, admin user, coupons)
```bash
python manage.py seed_data
```

### 4. Start the server
```bash
python manage.py runserver
```

### 5. Open in browser
- **App:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin/
  - Username: `admin` | Password: `admin123`

---

## ✅ Features

### 🔐 Authentication
- User Registration & Login
- Session-based auth with Django
- Profile page with order history

### 🛍️ Product Management
- Categories & Subcategories
- Product listing with pagination
- Real-time search (Fetch API)
- Product detail pages with reviews & ratings
- Stock management
- Discount badges

### 🛒 Cart System
- Add / Remove items
- +/- quantity buttons (AJAX – no page reload)
- Auto price update
- Cart persisted per user in DB

### ❤️ Wishlist
- Heart icon toggle (AJAX)
- Dedicated wishlist page
- Count badge in navbar

### 💳 Checkout & Orders
- Address management (add/select multiple)
- Coupon system (WELCOME20, SAVE50)
- Order placement with stock deduction
- Order status tracking (Pending → Confirmed → Delivered)
- Estimated delivery time display

### 🎛️ Admin Panel
- Manage Products, Categories, Orders, Users
- Inline order items editing
- Order status update

### 💡 UI/UX
- White & Yellow QuickCart theme
- Responsive design (mobile-friendly)
- Toast notifications for all cart/wishlist actions
- Auto-sliding hero banner
- Sticky navbar with cart/wishlist badges

---

## 🗂️ Project Structure

```
quickcart/
├── manage.py
├── requirements.txt
├── quickcart/          # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/              # Main app
│   ├── models.py       # DB models
│   ├── views.py        # All views + AJAX APIs
│   ├── urls.py         # URL routing
│   ├── forms.py        # Django forms
│   ├── admin.py        # Admin config
│   ├── context_processors.py
│   └── management/commands/seed_data.py
├── templates/
│   ├── base.html
│   ├── registration/
│   │   ├── login.html
│   │   └── register.html
│   └── store/
│       ├── home.html
│       ├── product_list.html
│       ├── product_detail.html
│       ├── cart.html
│       ├── wishlist.html
│       ├── checkout.html
│       ├── order_list.html
│       ├── order_detail.html
│       ├── profile.html
│       └── includes/product_card.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── media/              # Uploaded files (auto-created)
```

---

## 🗄️ Database Models

| Model | Fields |
|---|---|
| Category | name, image, slug |
| Product | name, category, price, discount, stock, description, image |
| Cart / CartItem | user, product, quantity |
| Wishlist | user, product |
| Address | user, house_no, street, city, pincode |
| Order / OrderItem | user, address, total, status, coupon |
| Coupon | code, discount_percent, min_order_amount |
| Review | product, user, rating, comment |

---

## 🔌 API Endpoints

| Method | URL | Description |
|---|---|---|
| POST | `/cart/add/<id>/` | Add product to cart |
| POST | `/cart/update/<id>/` | Increment/Decrement qty |
| POST | `/cart/remove/<id>/` | Remove item from cart |
| POST | `/wishlist/toggle/<id>/` | Toggle wishlist |
| POST | `/checkout/apply-coupon/` | Apply coupon code |

All return JSON. CSRF protected.

---

## 🎟️ Demo Coupons
- `WELCOME20` – 20% off on orders ₹100+
- `SAVE50` – 10% off on orders ₹500+

---

## 🛡️ Security
- CSRF tokens on all forms and AJAX
- Login required for cart/checkout/wishlist
- Django password hashing
- Form validation on all inputs

---

## 🔧 Tech Stack
- **Backend:** Django 4.2 (Python)
- **Frontend:** HTML5, CSS3, Vanilla JS (Fetch API)
- **Database:** SQLite (switch to MySQL by updating settings.py)
- **Auth:** Django built-in authentication
