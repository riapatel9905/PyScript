from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from extensions import db
from models import CartItem, MenuItem, Store
from blueprints.cart import haversine_km

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _cart_payload():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(ci.subtotal for ci in items)
    return {
        "items": [
            {
                "cart_item_id": ci.id,
                "menu_item_id": ci.menu_item_id,
                "name": ci.menu_item.name,
                "price": ci.menu_item.price,
                "image": ci.menu_item.image,
                "quantity": ci.quantity,
                "subtotal": ci.subtotal,
            }
            for ci in items
        ],
        "count": sum(ci.quantity for ci in items),
        "subtotal": subtotal,
    }


@api_bp.route("/cart", methods=["GET"])
@login_required
def get_cart():
    return jsonify(_cart_payload())


@api_bp.route("/cart/add", methods=["POST"])
@login_required
def add_to_cart():
    data = request.get_json(silent=True) or request.form
    try:
        menu_item_id = int(data.get("menu_item_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "menu_item_id is required"}), 400
    quantity = int(data.get("quantity", 1) or 1)
    quantity = max(1, quantity)

    item = MenuItem.query.get(menu_item_id)
    if not item or not item.is_available:
        return jsonify({"error": "Item not available"}), 404

    ci = CartItem.query.filter_by(user_id=current_user.id, menu_item_id=menu_item_id).first()
    if ci:
        ci.quantity += quantity
    else:
        ci = CartItem(user_id=current_user.id, menu_item_id=menu_item_id, quantity=quantity)
        db.session.add(ci)
    db.session.commit()
    return jsonify(_cart_payload())


@api_bp.route("/cart/update", methods=["POST"])
@login_required
def update_cart():
    data = request.get_json(silent=True) or request.form
    cart_item_id = data.get("cart_item_id")
    quantity = data.get("quantity")
    try:
        cart_item_id = int(cart_item_id)
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({"error": "cart_item_id and quantity are required"}), 400

    ci = CartItem.query.filter_by(id=cart_item_id, user_id=current_user.id).first()
    if not ci:
        return jsonify({"error": "Cart item not found"}), 404

    if quantity <= 0:
        db.session.delete(ci)
    else:
        ci.quantity = quantity
    db.session.commit()
    return jsonify(_cart_payload())


@api_bp.route("/cart/delete", methods=["POST"])
@login_required
def delete_cart_item():
    data = request.get_json(silent=True) or request.form
    try:
        cart_item_id = int(data.get("cart_item_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "cart_item_id is required"}), 400

    ci = CartItem.query.filter_by(id=cart_item_id, user_id=current_user.id).first()
    if ci:
        db.session.delete(ci)
        db.session.commit()
    return jsonify(_cart_payload())


@api_bp.route("/cart/update-by-item", methods=["POST"])
@login_required
def update_cart_by_item():
    """Set the absolute quantity in the cart for a given menu item.
    Used by the menu page's +/- qty controls."""
    data = request.get_json(silent=True) or request.form
    try:
        menu_item_id = int(data.get("menu_item_id"))
        quantity = int(data.get("quantity"))
    except (TypeError, ValueError):
        return jsonify({"error": "menu_item_id and quantity are required"}), 400

    ci = CartItem.query.filter_by(user_id=current_user.id, menu_item_id=menu_item_id).first()
    if quantity <= 0:
        if ci:
            db.session.delete(ci)
    else:
        item = MenuItem.query.get(menu_item_id)
        if not item or not item.is_available:
            return jsonify({"error": "Item not available"}), 404
        if ci:
            ci.quantity = quantity
        else:
            db.session.add(CartItem(user_id=current_user.id, menu_item_id=menu_item_id, quantity=quantity))
    db.session.commit()
    return jsonify(_cart_payload())


@api_bp.route("/nearest-store", methods=["GET"])
@login_required
def nearest_store():
    try:
        lat = float(request.args.get("lat"))
        lng = float(request.args.get("lng"))
    except (TypeError, ValueError):
        return jsonify({"error": "lat and lng query params are required"}), 400

    stores = Store.query.filter_by(is_active=True).all()
    if not stores:
        return jsonify({"error": "No stores available"}), 404

    ranked = sorted(
        stores, key=lambda s: haversine_km(lat, lng, s.latitude, s.longitude)
    )
    nearest = ranked[0]
    distance_km = round(haversine_km(lat, lng, nearest.latitude, nearest.longitude), 2)
    payload = nearest.to_dict()
    payload["distance_km"] = distance_km
    payload["all_ranked"] = [
        {**s.to_dict(), "distance_km": round(haversine_km(lat, lng, s.latitude, s.longitude), 2)}
        for s in ranked
    ]
    return jsonify(payload)
