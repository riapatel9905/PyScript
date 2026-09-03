import json
import os

from extensions import db
from models import MenuItem, Store, User

BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Coordinates taken from the Google Maps embeds already present in the
# original franchises.html for each of the three real branches.
STORES = [
    {
        "name": "Paldi Branch",
        "address": "Under Dr Babasaheb Ambedkar Brg, Narayan Nagar Society, "
                    "Ranna Park, Paldi, Ahmedabad, Gujarat 380007",
        "phone": "07874014330",
        "latitude": 22.997587,
        "longitude": 72.486591,
    },
    {
        "name": "Prahlad Nagar Garden, Anandnagar",
        "address": "G 1, Camps Corner, Opposite Prahlad Nagar Garden, "
                    "Prahlad Nagar, Ahmedabad-380015",
        "phone": "7096040628",
        "latitude": 23.011991,
        "longitude": 72.510559,
    },
    {
        "name": "TRP Mall, Bopal",
        "address": "R-11, Ground Floor of 5th Floor, TRP Mall The Retail Park "
                    "Rajyash City, Ghuma BRTS Road, Bopal, Ahmedabad, Gujarat 380058",
        "phone": "7486098481",
        "latitude": 23.031485,
        "longitude": 72.470210,
    },
]


def run_seed():
    if Store.query.count() == 0:
        for s in STORES:
            db.session.add(Store(**s))

    if MenuItem.query.count() == 0:
        seed_path = os.path.join(BASEDIR, "menu_seed.json")
        with open(seed_path, encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            db.session.add(MenuItem(
                name=entry["name"],
                category=entry["category"],
                description=entry["desc"],
                price=entry["price"],
                image=entry["image"],
                is_available=True,
            ))

    if User.query.filter_by(email="admin@pyscriptcafe.com").first() is None:
        admin = User(username="Admin", email="admin@pyscriptcafe.com",
                     phone="9999999999", is_admin=True,
                     address="Py-Script The Tech Cafe HQ")
        admin.set_password("Admin@123")
        db.session.add(admin)

    db.session.commit()
