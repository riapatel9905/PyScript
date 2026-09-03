from math import radians, sin, cos, sqrt, atan2

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import CartItem, Store, Order, OrderItem
from payments import validate_card, validate_upi

cart_bp = Blueprint("cart", __name__)


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


@cart_bp.route("/cart")
@login_required
def view_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(ci.subtotal for ci in items)
    return render_template("cart.html", items=items, subtotal=subtotal)


@cart_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Your cart is empty.", "info")
        return redirect(url_for("shop.menu"))

    subtotal = sum(ci.subtotal for ci in items)
    delivery_fee = 0 if subtotal >= 500 else 40
    total = subtotal + delivery_fee
    stores = Store.query.filter_by(is_active=True).all()

    if request.method == "POST":
        store_id = request.form.get("store_id", type=int)
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        pincode = request.form.get("pincode", "").strip()
        payment_method = request.form.get("payment_method", "")

        store = db.session.get(Store, store_id) if store_id else None
        errors = []
        if not name:
            errors.append("Please enter your full name.")
        if not phone:
            errors.append("Please enter your phone number.")
        if not store:
            errors.append("Please select a delivery store/branch.")
        if len(address) < 10:
            errors.append("Please enter a complete delivery address.")
        if not city:
            errors.append("Please enter your city.")
        if not pincode:
            errors.append("Please enter your pincode.")

        # The address textarea, city and pincode are collected as separate
        # fields in the UI but stored together as one delivery address, so
        # the store/dispatch team gets the full picture in one string.
        full_address = address
        if city or pincode:
            full_address = f"{address}, {city} - {pincode}".strip(", ")

        payment_last4 = None
        if payment_method == "card":
            card_number = request.form.get("card_number", "")
            expiry = request.form.get("expiry", "")
            cvv = request.form.get("cvv", "")
            ok, err = validate_card(card_number, expiry, cvv)
            if not ok:
                errors.append(err)
            else:
                payment_last4 = card_number.replace(" ", "")[-4:]
        elif payment_method == "upi":
            upi_id = request.form.get("upi_id", "")
            ok, err = validate_upi(upi_id)
            if not ok:
                errors.append(err)
            else:
                payment_last4 = upi_id
        elif payment_method == "cod":
            payment_last4 = "COD"
        else:
            errors.append("Please select a payment method.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "checkout.html", items=items, subtotal=subtotal,
                delivery_fee=delivery_fee, total=total, stores=stores,
                form=request.form, user=current_user,
            )

        order = Order(
            user_id=current_user.id,
            store_id=store.id,
            delivery_address=full_address,
            payment_method=payment_method,
            payment_last4=payment_last4,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total=total,
            status="placed",
        )
        db.session.add(order)
        db.session.flush()

        for ci in items:
            db.session.add(OrderItem(
                order_id=order.id,
                menu_item_id=ci.menu_item_id,
                name=ci.menu_item.name,
                price=ci.menu_item.price,
                image=ci.menu_item.image,
                quantity=ci.quantity,
            ))
            db.session.delete(ci)

        db.session.commit()
        flash("Order placed successfully!", "success")
        return redirect(url_for("orders.confirmation", order_id=order.id))

    return render_template(
        "checkout.html", items=items, subtotal=subtotal,
        delivery_fee=delivery_fee, total=total, stores=stores, form={},
        user=current_user,
    )
