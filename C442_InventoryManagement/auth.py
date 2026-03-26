from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from model import InventoryModel

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = "viewer"  # default role

        model = InventoryModel()

        # Check if user already exists
        existing = model.get_user_by_username(username)
        if existing:
            model.close()
            flash("Username already exists", "error")
            return redirect(url_for("auth.register"))

        # Hash password
        password_hash = generate_password_hash(password)

        # Create user
        model.create_user(username, password_hash, role)
        model.close()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        model = InventoryModel()
        row = model.get_user_by_username(username)
        user = model.build_user_object(row)
        model.close()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("inventory.index"))

        flash("Invalid username or password", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))