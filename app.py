import os
from flask import Flask
from flask_login import current_user

from extensions import db, login_manager
from models import User


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    elif os.environ.get("VERCEL"):
        import tempfile
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(tempfile.gettempdir(), "cafe.db")
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "cafe.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from blueprints.auth import auth_bp
    from blueprints.shop import shop_bp
    from blueprints.cart import cart_bp
    from blueprints.orders import orders_bp
    from blueprints.admin import admin_bp
    from blueprints.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_globals():
        cart_count = 0
        if current_user.is_authenticated:
            from models import CartItem
            cart_count = sum(
                ci.quantity for ci in CartItem.query.filter_by(user_id=current_user.id).all()
            )
        return {"cart_count": cart_count}

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("404.html"), 404

    with app.app_context():
        db.create_all()
        from seed import run_seed
        run_seed()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
