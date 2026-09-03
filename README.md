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
  payment gateway wired in**.
- **Order history & confirmation** pages per user.
- **Admin panel** (`/admin`, admin accounts only): dashboard with stats,
  full CRUD for menu items and branches, order list with status updates,
  and user management.
- A small **JSON API** (`/api/cart/*`, `/api/nearest-store`) that powers
  the cart and nearest-branch lookup.

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-Login
- Werkzeug
- HTML
- CSS
- JavaScript
- Bootstrap / Tailwind where applicable

## Running Locally

```bash
cd cafeapp
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py