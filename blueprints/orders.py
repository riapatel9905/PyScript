from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from models import Order

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/orders")
@login_required
def history():
    orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template("orders.html", orders=orders)


@orders_bp.route("/orders/<int:order_id>")
@login_required
def confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template("order_confirmation.html", order=order)
