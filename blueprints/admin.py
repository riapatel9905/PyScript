from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models import MenuItem, Store, Order, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

CATEGORIES = ["beverages", "signature", "food", "desserts"]
STATUSES = ["placed", "preparing", "out_for_delivery", "delivered", "cancelled"]


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "users": User.query.count(),
        "menu_items": MenuItem.query.count(),
        "stores": Store.query.count(),
        "orders": Order.query.count(),
        "revenue": db.session.query(db.func.coalesce(db.func.sum(Order.total), 0))
        .filter(Order.status != "cancelled").scalar(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    return render_template("admin/dashboard.html", stats=stats, recent_orders=recent_orders)


# ---------------- Menu management ----------------

@admin_bp.route("/menu")
@login_required
@admin_required
def menu_list():
    items = MenuItem.query.order_by(MenuItem.category, MenuItem.name).all()
    return render_template("admin/menu.html", items=items)


@admin_bp.route("/menu/new", methods=["GET", "POST"])
@admin_bp.route("/menu/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def menu_form(item_id=None):
    item = MenuItem.query.get_or_404(item_id) if item_id else None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "")
        description = request.form.get("description", "").strip()
        image = request.form.get("image", "").strip()
        is_available = bool(request.form.get("is_available"))
        try:
            price = int(request.form.get("price", 0))
        except ValueError:
            price = 0

        errors = []
        if not name:
            errors.append("Name is required.")
        if category not in CATEGORIES:
            errors.append("Choose a valid category.")
        if price <= 0:
            errors.append("Price must be greater than 0.")
        if not image:
            errors.append("Image filename is required (e.g. m1.jpg).")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/menu_form.html", item=item, form=request.form, categories=CATEGORIES)

        if item is None:
            item = MenuItem(name=name, category=category, description=description,
                             price=price, image=image, is_available=is_available)
            db.session.add(item)
            flash(f"Added new menu item '{name}'.", "success")
        else:
            item.name, item.category, item.description = name, category, description
            item.price, item.image, item.is_available = price, image, is_available
            flash(f"Updated menu item '{name}'.", "success")

        db.session.commit()
        return redirect(url_for("admin.menu_list"))

    return render_template("admin/menu_form.html", item=item, form={}, categories=CATEGORIES)


@admin_bp.route("/menu/<int:item_id>/delete", methods=["POST"])
@login_required
@admin_required
def menu_delete(item_id):
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f"Deleted menu item '{item.name}'.", "info")
    return redirect(url_for("admin.menu_list"))


# ---------------- Store management ----------------

@admin_bp.route("/stores")
@login_required
@admin_required
def store_list():
    stores = Store.query.order_by(Store.name).all()
    return render_template("admin/stores.html", stores=stores)


@admin_bp.route("/stores/new", methods=["GET", "POST"])
@admin_bp.route("/stores/<int:store_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def store_form(store_id=None):
    store = Store.query.get_or_404(store_id) if store_id else None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()
        phone = request.form.get("phone", "").strip()
        is_active = bool(request.form.get("is_active"))
        try:
            latitude = float(request.form.get("latitude"))
            longitude = float(request.form.get("longitude"))
        except (TypeError, ValueError):
            latitude = longitude = None

        errors = []
        if not name:
            errors.append("Name is required.")
        if not address:
            errors.append("Address is required.")
        if latitude is None or longitude is None or not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            errors.append("Enter valid latitude/longitude coordinates.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/store_form.html", store=store, form=request.form)

        if store is None:
            store = Store(name=name, address=address, phone=phone,
                          latitude=latitude, longitude=longitude, is_active=is_active)
            db.session.add(store)
            flash(f"Added new branch '{name}'.", "success")
        else:
            store.name, store.address, store.phone = name, address, phone
            store.latitude, store.longitude, store.is_active = latitude, longitude, is_active
            flash(f"Updated branch '{name}'.", "success")

        db.session.commit()
        return redirect(url_for("admin.store_list"))

    return render_template("admin/store_form.html", store=store, form={})


@admin_bp.route("/stores/<int:store_id>/delete", methods=["POST"])
@login_required
@admin_required
def store_delete(store_id):
    store = Store.query.get_or_404(store_id)
    db.session.delete(store)
    db.session.commit()
    flash(f"Deleted branch '{store.name}'.", "info")
    return redirect(url_for("admin.store_list"))


# ---------------- Orders management ----------------

@admin_bp.route("/orders")
@login_required
@admin_required
def order_list():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=orders)


@admin_bp.route("/orders/<int:order_id>")
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("admin/order_detail.html", order=order, statuses=STATUSES)


@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
@admin_required
def order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get("status")
    if status in STATUSES:
        order.status = status
        db.session.commit()
        flash(f"Order #{order.id} marked as {status.replace('_', ' ')}.", "success")
    return redirect(url_for("admin.order_detail", order_id=order.id))


# ---------------- User management (view + toggle admin) ----------------

@admin_bp.route("/users")
@login_required
@admin_required
def user_list():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot change your own admin status.", "danger")
        return redirect(url_for("admin.user_list"))
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"Updated admin status for {user.username}.", "success")
    return redirect(url_for("admin.user_list"))
