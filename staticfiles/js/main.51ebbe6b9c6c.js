//  CSRF Helper 
function getCookie(name) {
  let val = null;
  document.cookie.split(';').forEach(c => {
    c = c.trim();
    if (c.startsWith(name + '=')) val = decodeURIComponent(c.slice(name.length + 1));
  });

  return val;
}

// Toast Notifications 
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');

  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || '✅'}</span> ${message}`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOut .3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Update Cart Badge ──
function updateCartBadge(count) {
  document.querySelectorAll('.cart-badge').forEach(el => {
    el.textContent = count;
    el.style.display = count > 0 ? 'flex' : 'none';
  });
}

// Add to Cart 
function addToCart(productId, btn) {
  fetch(`/cart/add/${productId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
  })
  .then(r => r.json())
  .then(data => {

    if (data.success) {
      showToast(data.message, 'success');
      updateCartBadge(data.cart_count);
      // Replace add button with qty control

      const addArea = btn.closest('.add-area');
      if (addArea) renderQtyControl(addArea, productId, data.quantity);
    }
  })
  .catch(() => showToast('Something went wrong', 'error'));
}

// Render Qty Control 
function renderQtyControl(container, productId, qty) {
  container.innerHTML = `
    <div class="qty-control" id="qty-${productId}">
      <button onclick="changeQty(${productId}, 'decrement', this)" title="Decrease">−</button>
      <span id="qty-val-${productId}">${qty}</span>
      <button onclick="changeQty(${productId}, 'increment', this)" title="Increase">+</button>
    </div>`;
}

// Change Quantity (product cards) 
function changeQty(productId, action, btn) {
  // Find CartItem ID from data attr on qty control parent
  const qtyEl = document.getElementById(`qty-${productId}`);
  const itemId = qtyEl ? qtyEl.dataset.itemId : null;
  if (!itemId) {
    // No item id yet — need to call add to cart once
    return;
  }
  fetch(`/cart/update/${itemId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
    body: JSON.stringify({ action })
  })
  .then(r => r.json())
  .then(data => {

    if (data.removed) {
      const addArea = btn.closest('.add-area');
      if (addArea) {
        addArea.innerHTML = `<button class="btn-add" onclick="addToCart(${productId}, this)">Add</button>`;
      }
      updateCartBadge(data.cart_count);
    } else {
      document.getElementById(`qty-val-${productId}`).textContent = data.quantity;
      updateCartBadge(data.cart_count);
    }
  })
  .catch(() => showToast('Something went wrong', 'error'));
}

// Cart Page Quantity 
function cartUpdate(itemId, action) {

  fetch(`/cart/update/${itemId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
    body: JSON.stringify({ action })
  })
  .then(r => r.json())
  .then(data => {

    if (data.removed) {
      document.getElementById(`cart-item-${itemId}`)?.remove();
      updateCartPageTotal(data.cart_total, data.cart_count);
      if (data.cart_count === 0) location.reload();
    } else {

      const row = document.getElementById(`cart-item-${itemId}`);

      if (row) {
        row.querySelector('.cart-qty-val').textContent = data.quantity;
        row.querySelector('.cart-item-subtotal').textContent = `₹${parseFloat(data.subtotal).toFixed(2)}`;
      }

      updateCartPageTotal(data.cart_total, data.cart_count);
    }
  })
  .catch(() => showToast('Error updating cart', 'error'));
}

function removeCartItem(itemId) {

  fetch(`/cart/remove/${itemId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken') }
  })
  .then(r => r.json())
  .then(data => {

    document.getElementById(`cart-item-${itemId}`)?.remove();
    updateCartPageTotal(data.cart_total, data.cart_count);
    
    if (data.cart_count === 0) location.reload();
    showToast('Item removed', 'info');
  });
}

function updateCartPageTotal(total, count) {
  const el = document.getElementById('cart-total');
  
  if (el) el.textContent = `₹${parseFloat(total).toFixed(2)}`;
  updateCartBadge(count);
}

// Wishlist Toggle 
function toggleWishlist(productId, btn) {
  const isLoggedIn = document.body.dataset.loggedIn === 'true';
  
  if (!isLoggedIn) {
    window.location.href = '/login/?next=' + window.location.pathname;
    return;
  }
  
  fetch(`/wishlist/toggle/${productId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken') }
  })
  .then(r => r.json())
  .then(data => {

    if (data.in_wishlist) {
      btn.classList.add('active');
      btn.title = 'Remove from wishlist';
    } else {
      btn.classList.remove('active');
      btn.title = 'Add to wishlist';
    }
    showToast(data.message, data.in_wishlist ? 'success' : 'info');
    // Update wishlist badge
    document.querySelectorAll('.wishlist-badge').forEach(el => {
      el.textContent = parseInt(el.textContent || 0) + (data.in_wishlist ? 1 : -1);
    });
  })
  .catch(() => showToast('Error updating wishlist', 'error'));
}

// Real-time Search 
const searchInput = document.getElementById('nav-search');

if (searchInput) {
  let debounceTimer;
  searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      const q = searchInput.value.trim();

      if (q.length > 1) {
        window.location.href = `/search/?q=${encodeURIComponent(q)}`;
      }
    }, 600);
  });
  searchInput.addEventListener('keydown', e => {

    if (e.key === 'Enter') {
      e.preventDefault();
      const q = searchInput.value.trim();

      if (q) window.location.href = `/search/?q=${encodeURIComponent(q)}`;
    }
  });
}

// Coupon Apply 
const couponBtn = document.getElementById('apply-coupon-btn');

if (couponBtn) {
  couponBtn.addEventListener('click', () => {
    const code = document.getElementById('coupon-input').value.trim();

    if (!code) return;
    fetch('/checkout/apply-coupon/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    })
    .then(r => r.json())
    .then(data => {

      showToast(data.message, data.success ? 'success' : 'error');
      if (data.success) {
        document.getElementById('discount-row').style.display = 'flex';
        document.getElementById('discount-amount').textContent = `₹${data.discount.toFixed(2)}`;
        document.getElementById('final-total').textContent = `₹${data.final_total.toFixed(2)}`;
        document.getElementById('hidden-coupon').value = code;
      }
    });
  });
}

// Banner Slider 
const bannerSlides = document.querySelectorAll('.banner-slide');
if (bannerSlides.length > 1) {
  
  let current = 0;
  function showSlide(n) {
    bannerSlides.forEach((s, i) => s.style.opacity = i === n ? '1' : '0');
  }

  showSlide(0);
  setInterval(() => { current = (current + 1) % bannerSlides.length; showSlide(current); }, 3500);
}

// clears localStorage
let loc = localStorage.getItem("location");

if (loc && loc !== "null" && loc !== "undefined" && loc.trim() !== "") {
    window.location.href = loc;
}

function saveLocation(value) {
    if (value && value !== "null" && value !== "undefined") {
        localStorage.setItem("location", value);
    }
}





