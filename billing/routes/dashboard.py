from flask import Blueprint, render_template
from flask_login import login_required
from models import Invoice, Client, Payment
from sqlalchemy import func

dash_bp = Blueprint("dashboard", __name__)


@dash_bp.route("/")
@login_required
def index():
    total_invoices = Invoice.query.count()
    paid_count = Invoice.query.filter_by(status="paid").count()
    unpaid_count = Invoice.query.filter_by(status="unpaid").count()
    partial_count = Invoice.query.filter_by(status="partial").count()
    total_clients = Client.query.count()

    recent_invoices = (
        Invoice.query.order_by(Invoice.created_at.desc()).limit(8).all()
    )

    # Revenue = sum of all payments received
    total_received = (
        Payment.query.with_entities(func.sum(Payment.amount)).scalar() or 0.0
    )

    return render_template(
        "dashboard.html",
        total_invoices=total_invoices,
        paid_count=paid_count,
        unpaid_count=unpaid_count,
        partial_count=partial_count,
        total_clients=total_clients,
        recent_invoices=recent_invoices,
        total_received=total_received,
    )
