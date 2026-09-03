# Py-Script The Tech Cafe — Full-Stack Ordering Website

A complete Flask e-commerce site built on top of your original static
design (logo, images, colour palette, login/signup layout). Real menu
items and the 3 real branch locations were pulled directly out of your
uploaded `menu.html` / `franchises.html`.

## What's included

- **Landing / Get Started page** → **Sign up / Log in** (hashed passwords,
  session auth via Flask-Login) → shop opens.
- **Home & Menu** pages with all 26 real menu items across Beverages,
  Signature, Food, and Desserts, with "Add to Cart".
- **Cart**: live quantity edit / update / delete, item images, running
  subtotal — all via a small JSON API, no page reloads.
- **Nearest-branch delivery**: at checkout you can tap "Use my location"
  — the browser's geolocation is sent to `/api/nearest-store`, which
  calculates the closest of your 3 real branches (haversine distance)
  and auto-selects it. You can still pick a branch manually.
- **Checkout**: delivery address, and payment method — Credit Card,
  Debit Card, UPI, or Cash on Delivery. Card numbers are checksum-validated
  (Luhn algorithm) and only the last 4 digits are ever stored; UPI IDs are
  format-validated. **This is local validation only — there is no real
  payment gateway wired in** (that requires your own merchant account
  and API keys with a provider like Razorpay/Stripe/PayU; happy to wire
  one in if you get credentials).
- **Order history & confirmation** pages per user.
- **Admin panel** (`/admin`, admin accounts only): dashboard with stats,
  full CRUD for menu items and branches, order list with status updates
  (placed → preparing → out for delivery → delivered / cancelled), and
  user management (view + promote/demote admins).
- A small **JSON API** (`/api/cart/*`, `/api/nearest-store`) that powers
  the cart and the nearest-branch lookup, reusable by a future mobile app.

## Tech stack

Flask, Flask-SQLAlchemy (SQLite), Flask-Login, Werkzeug password hashing.
No frontend framework — vanilla JS (`static/js/main.js`) for the AJAX
cart/checkout behaviour, styled with a new `static/css/app.css` that
matches your original black/gold/Poppins look.

## Running it locally

```bash
cd cafeapp
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000**. The database (`cafe.db`) and all
menu items / branches / a demo admin account are created automatically
on first run.

### Demo admin login
- Email: `admin@pyscriptcafe.com`
- Password: `Admin@123`

**Change or remove this account before deploying anywhere public.**

## Project structure

```
cafeapp/
├── app.py                  # App factory, DB init, blueprint registration
├── extensions.py           # db / login_manager singletons
├── models.py                # User, Store, MenuItem, CartItem, Order, OrderItem
├── payments.py              # Luhn card validation, UPI validation
├── seed.py + menu_seed.json # First-run seed data (real menu + branches)
├── requirements.txt
├── blueprints/
│   ├── auth.py       # landing, signup, login, logout
│   ├── shop.py       # home, menu, franchises
│   ├── cart.py       # cart page, checkout page + order placement
│   ├── orders.py     # order history, confirmation
│   ├── admin.py       # admin dashboard + all CRUD
│   └── api.py         # JSON API: cart mutations, nearest-store
├── templates/          # Jinja templates (extends base.html)
│   └── admin/           # admin panel templates
└── static/
    ├── css/app.css       # new site-wide styling
    ├── css/login.css, signup.css  # from your original design
    ├── img/               # your original logo + menu/branch photos
    └── js/main.js         # cart AJAX, geolocation, payment tabs
```

## What I'd suggest doing next

1. **Real payment gateway** — if you want actual charges to go through,
   get a Razorpay or Stripe account (both work well in India for UPI +
   cards) and I can wire their SDK in place of the local validation.
2. **Production database** — swap SQLite for Postgres/MySQL before you
   get real traffic; SQLAlchemy makes that a one-line config change.
3. **Deploy** — this is ready to deploy as-is to something like Render,
   Railway, or a VPS with gunicorn + nginx in front.
4. **Image uploads in admin** — right now the admin menu form takes an
   image *filename* (from `static/img`); could be upgraded to an actual
   file upload if you want to add new photos through the UI.
