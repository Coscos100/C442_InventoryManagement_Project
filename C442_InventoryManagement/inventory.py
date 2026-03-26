from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from model import InventoryModel
from flask import jsonify
inventory_bp = Blueprint("inventory", __name__)


def role_required(*roles):
    """
    Only allow users whose role is in roles.
    Example:
    @role_required("admin")
    @role_required("admin", "editor")
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            if current_user.role not in roles:
                abort(403)

            return f(*args, **kwargs)
        return wrapped
    return decorator


def get_categories():
    return [
        "Electronics",
        "Computers & Accessories",
        "Mobile Phones & Tablets",
        "Audio & Headphones",
        "Home Appliances",
        "Furniture",
        "Office Supplies",
        "Clothing & Apparel",
        "Footwear",
        "Books & Media",
        "Toys & Games",
        "Sports & Outdoors",
        "Health & Personal Care",
        "Beauty & Cosmetics",
        "Food & Beverages",
        "Automotive",
        "Tools & Hardware",
        "Garden & Outdoor",
        "Pet Supplies",
        "Miscellaneous"
    ]


@inventory_bp.route("/")
@login_required
def index():
    search = request.args.get("search", "").strip()

    model = InventoryModel()
    if search:
        products = model.get_product(search)
    else:
        products = model.get_all_products()
    model.close()

    return render_template(
        "index.html",
        products=products,
        categories=get_categories(),
        search=search
    )


@inventory_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required("admin", "editor")
def add_product():
    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        quantity = request.form.get("quantity")
        category = request.form.get("category")

        model = InventoryModel()
        model.add_product(name, float(price), int(quantity), category)
        model.close()

        return redirect(url_for("inventory.index"))

    return render_template("add_product.html", categories=get_categories())


@inventory_bp.route("/update/<int:product_id>", methods=["POST"])
@login_required
@role_required("admin", "editor")
def update_product(product_id):
    search = request.args.get("search", "").strip()

    name = request.form.get("name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")
    category = request.form.get("category")

    model = InventoryModel()
    model.update_product(product_id, name, float(price), int(quantity), category)
    model.close()

    return redirect(url_for("inventory.index", search=search))


@inventory_bp.route("/delete/<int:product_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete_product(product_id):
    search = request.args.get("search", "").strip()

    model = InventoryModel()
    model.delete_product(product_id)
    model.close()

    return redirect(url_for("inventory.index", search=search))


@inventory_bp.route("/category-data")
@login_required
def category_data():
    model = InventoryModel()
    data = model.get_quantity_by_category()
    model.close()
    return jsonify(data)

@inventory_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@inventory_bp.route("/category-value-data")
@login_required
def category_value_data():
    """
    Returns total inventory value per category as JSON
    """
    model = InventoryModel()
    model.cursor.execute("""
        SELECT Category, COALESCE(SUM(Price * Quantity), 0) AS total_value
        FROM Product
        GROUP BY Category
    """)
    data = model.cursor.fetchall()
    model.close()
    # Return as list of dicts
    return jsonify(data)