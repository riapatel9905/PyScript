from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import MenuItem, Store, CartItem

shop_bp = Blueprint("shop", __name__)


@shop_bp.route("/home")
@login_required
def home():
    featured = MenuItem.query.filter_by(is_available=True).limit(8).all()
    stores = Store.query.filter_by(is_active=True).all()
    return render_template("home.html", featured=featured, stores=stores)


@shop_bp.route("/menu")
@login_required
def menu():
    categories = ["beverages", "signature", "food", "desserts"]
    items_by_category = {
        cat: MenuItem.query.filter_by(category=cat, is_available=True).all()
        for cat in categories
    }
    cart_qty_map = {
        ci.menu_item_id: ci.quantity
        for ci in CartItem.query.filter_by(user_id=current_user.id).all()
    }
    return render_template(
        "menu.html", items_by_category=items_by_category, cart_qty_map=cart_qty_map
    )


@shop_bp.route("/about")
@login_required
def about():
    return render_template("about.html")


@shop_bp.route("/contactus")
@login_required
def contactus():
    return render_template("contactus.html")


@shop_bp.route("/feedback")
@login_required
def feedback():
    return render_template("feedback.html")


@shop_bp.route("/franchises")
@login_required
def franchises():
    stores = Store.query.filter_by(is_active=True).all()
    return render_template("franchises.html", stores=stores)
