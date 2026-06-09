from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import db, Client

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")


@clients_bp.route("/")
@login_required
def list_clients():
    q = request.args.get("q", "").strip()
    query = Client.query
    if q:
        query = query.filter(Client.name.ilike(f"%{q}%"))
    clients = query.order_by(Client.name).all()
    return render_template("clients/list.html", clients=clients, q=q)


@clients_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Client name is required.", "danger")
            return render_template("clients/form.html", client=None)
        client = Client(
            name=name,
            address=request.form.get("address", "").strip(),
            phone=request.form.get("phone", "").strip(),
            email=request.form.get("email", "").strip(),
            pan=request.form.get("pan", "").strip(),
        )
        db.session.add(client)
        db.session.commit()
        flash(f'Client "{client.name}" added.', "success")
        return redirect(url_for("clients.list_clients"))
    return render_template("clients/form.html", client=None)


@clients_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    client = Client.query.get_or_404(id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Client name is required.", "danger")
            return render_template("clients/form.html", client=client)
        client.name = name
        client.address = request.form.get("address", "").strip()
        client.phone = request.form.get("phone", "").strip()
        client.email = request.form.get("email", "").strip()
        client.pan = request.form.get("pan", "").strip()
        db.session.commit()
        flash("Client updated.", "success")
        return redirect(url_for("clients.list_clients"))
    return render_template("clients/form.html", client=client)


@clients_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    client = Client.query.get_or_404(id)
    if client.invoices:
        flash("Cannot delete a client with existing invoices.", "danger")
    else:
        db.session.delete(client)
        db.session.commit()
        flash("Client deleted.", "success")
    return redirect(url_for("clients.list_clients"))
