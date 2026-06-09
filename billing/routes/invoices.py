import io
from datetime import datetime, date
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, send_file, current_app)
from flask_login import login_required
from models import db, Invoice, InvoiceItem, Client, Payment
from utils import next_invoice_no, amount_to_words

invoices_bp = Blueprint("invoices", __name__, url_prefix="/invoices")


def _parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _save_items(invoice, form):
    InvoiceItem.query.filter_by(invoice_id=invoice.id).delete()
    descriptions = form.getlist("description[]")
    hs_codes = form.getlist("hs_code[]")
    qtys = form.getlist("qty[]")
    units = form.getlist("unit[]")
    rates = form.getlist("rate[]")
    sno = 0
    for i, desc in enumerate(descriptions):
        if not desc.strip():
            continue
        sno += 1
        item = InvoiceItem(
            invoice_id=invoice.id,
            sno=sno,
            hs_code=(hs_codes[i] if i < len(hs_codes) else "-") or "-",
            description=desc.strip(),
            qty=float(qtys[i]) if i < len(qtys) and qtys[i] else 1.0,
            unit=(units[i] if i < len(units) else "Job") or "Job",
            rate=float(rates[i]) if i < len(rates) and rates[i] else 0.0,
        )
        db.session.add(item)


@invoices_bp.route("/")
@login_required
def list_invoices():
    status = request.args.get("status", "")
    q = request.args.get("q", "").strip()
    query = Invoice.query.join(Client)
    if status:
        query = query.filter(Invoice.status == status)
    if q:
        query = query.filter(
            Client.name.ilike(f"%{q}%") | Invoice.invoice_no.ilike(f"%{q}%")
        )
    invoices = query.order_by(Invoice.created_at.desc()).all()
    return render_template("invoices/list.html", invoices=invoices,
                           status=status, q=q)


@invoices_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    clients = Client.query.order_by(Client.name).all()
    inv_no = next_invoice_no(Invoice)
    today = date.today()

    if request.method == "POST":
        client_id = request.form.get("client_id")
        if not client_id:
            flash("Please select a client.", "danger")
            return render_template("invoices/form.html", clients=clients,
                                   invoice=None, inv_no=inv_no, today=today)

        invoice = Invoice(
            invoice_no=request.form.get("invoice_no", inv_no).strip() or inv_no,
            client_id=int(client_id),
            issue_date=_parse_date(request.form.get("issue_date")) or today,
            due_date=_parse_date(request.form.get("due_date")),
            payment_mode=request.form.get("payment_mode", "Bank Account"),
            reference=request.form.get("reference", "").strip(),
            notes=request.form.get("notes", "").strip(),
            status="unpaid",
        )
        db.session.add(invoice)
        db.session.flush()
        _save_items(invoice, request.form)
        db.session.commit()
        flash(f"Invoice {invoice.invoice_no} created.", "success")
        return redirect(url_for("invoices.view", id=invoice.id))

    return render_template("invoices/form.html", clients=clients,
                           invoice=None, inv_no=inv_no, today=today)


@invoices_bp.route("/<int:id>")
@login_required
def view(id):
    invoice = Invoice.query.get_or_404(id)
    in_words = amount_to_words(invoice.total)
    return render_template("invoices/view.html", invoice=invoice,
                           in_words=in_words)


@invoices_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    invoice = Invoice.query.get_or_404(id)
    clients = Client.query.order_by(Client.name).all()

    if request.method == "POST":
        client_id = request.form.get("client_id")
        if not client_id:
            flash("Please select a client.", "danger")
            return render_template("invoices/form.html", clients=clients,
                                   invoice=invoice, inv_no=invoice.invoice_no,
                                   today=date.today())

        invoice.invoice_no = request.form.get("invoice_no", invoice.invoice_no).strip()
        invoice.client_id = int(client_id)
        invoice.issue_date = _parse_date(request.form.get("issue_date")) or invoice.issue_date
        invoice.due_date = _parse_date(request.form.get("due_date"))
        invoice.payment_mode = request.form.get("payment_mode", "Bank Account")
        invoice.reference = request.form.get("reference", "").strip()
        invoice.notes = request.form.get("notes", "").strip()
        invoice.updated_at = datetime.utcnow()
        _save_items(invoice, request.form)
        invoice.refresh_status()
        db.session.commit()
        flash("Invoice updated.", "success")
        return redirect(url_for("invoices.view", id=invoice.id))

    return render_template("invoices/form.html", clients=clients,
                           invoice=invoice, inv_no=invoice.invoice_no,
                           today=date.today())


@invoices_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    invoice = Invoice.query.get_or_404(id)
    db.session.delete(invoice)
    db.session.commit()
    flash("Invoice deleted.", "success")
    return redirect(url_for("invoices.list_invoices"))


@invoices_bp.route("/<int:id>/payment", methods=["POST"])
@login_required
def add_payment(id):
    invoice = Invoice.query.get_or_404(id)
    try:
        amount = round(float(request.form.get("amount", 0)), 2)
    except ValueError:
        amount = 0.0
    if amount <= 0:
        flash("Enter a valid payment amount.", "danger")
        return redirect(url_for("invoices.view", id=id))

    payment = Payment(
        invoice_id=invoice.id,
        amount=amount,
        date=_parse_date(request.form.get("date")) or date.today(),
        method=request.form.get("method", "").strip(),
        notes=request.form.get("notes", "").strip(),
    )
    db.session.add(payment)
    db.session.flush()
    invoice.refresh_status()
    db.session.commit()
    flash(f"Payment of NPR {amount:,.2f} recorded.", "success")
    return redirect(url_for("invoices.view", id=id))


@invoices_bp.route("/<int:id>/payment/<int:pid>/delete", methods=["POST"])
@login_required
def delete_payment(id, pid):
    payment = Payment.query.get_or_404(pid)
    invoice = Invoice.query.get_or_404(id)
    db.session.delete(payment)
    db.session.flush()
    invoice.refresh_status()
    db.session.commit()
    flash("Payment record removed.", "success")
    return redirect(url_for("invoices.view", id=id))


@invoices_bp.route("/<int:id>/pdf")
@login_required
def generate_pdf(id):
    invoice = Invoice.query.get_or_404(id)
    in_words = amount_to_words(invoice.total)
    html_str = render_template("invoices/pdf_template.html",
                                invoice=invoice, in_words=in_words)
    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html_str,
                         base_url=current_app.root_path).write_pdf()
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=False,
            download_name=f"{invoice.invoice_no}.pdf",
        )
    except Exception:
        # Graceful fallback: printable HTML page
        return render_template("invoices/pdf_template.html",
                               invoice=invoice, in_words=in_words,
                               print_mode=True)
