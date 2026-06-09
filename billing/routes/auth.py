from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(request.args.get("next") or url_for("dashboard.index"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/users")
@login_required
def users():
    from flask import abort
    if current_user.role != "admin":
        abort(403)
    all_users = User.query.order_by(User.username).all()
    return render_template("users/list.html", users=all_users)


@auth_bp.route("/users/new", methods=["GET", "POST"])
@login_required
def create_user():
    from flask import abort
    if current_user.role != "admin":
        abort(403)
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "staff")
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
        else:
            u = User(username=username, email=email, role=role)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            flash(f"User '{username}' created.", "success")
            return redirect(url_for("auth.users"))
    return render_template("users/form.html", user=None)


@auth_bp.route("/users/<int:id>/delete", methods=["POST"])
@login_required
def delete_user(id):
    from flask import abort
    if current_user.role != "admin":
        abort(403)
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash("Cannot delete your own account.", "danger")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", "success")
    return redirect(url_for("auth.users"))
