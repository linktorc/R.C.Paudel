from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="staff")   # "admin" | "staff"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), default="")
    phone = db.Column(db.String(50), default="")
    email = db.Column(db.String(120), default="")
    pan = db.Column(db.String(20), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoices = db.relationship("Invoice", backref="client", lazy=True)

    def __repr__(self):
        return f"<Client {self.name}>"


class Invoice(db.Model):
    __tablename__ = "invoices"
    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(50), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    issue_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date)
    payment_mode = db.Column(db.String(50), default="Bank Account")
    reference = db.Column(db.String(200), default="")
    notes = db.Column(db.Text, default="")
    # "unpaid" | "partial" | "paid"
    status = db.Column(db.String(20), default="unpaid")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship(
        "InvoiceItem", backref="invoice", lazy=True,
        cascade="all, delete-orphan", order_by="InvoiceItem.sno"
    )
    payments = db.relationship(
        "Payment", backref="invoice", lazy=True,
        cascade="all, delete-orphan", order_by="Payment.date"
    )

    @property
    def subtotal(self) -> float:
        return round(sum(i.amount for i in self.items), 2)

    @property
    def vat(self) -> float:
        return round(self.subtotal * 0.13, 2)

    @property
    def total(self) -> float:
        return round(self.subtotal + self.vat, 2)

    @property
    def amount_paid(self) -> float:
        return round(sum(p.amount for p in self.payments), 2)

    @property
    def balance_due(self) -> float:
        return round(self.total - self.amount_paid, 2)

    def refresh_status(self):
        paid = self.amount_paid
        if paid <= 0:
            self.status = "unpaid"
        elif paid >= self.total:
            self.status = "paid"
        else:
            self.status = "partial"

    def __repr__(self):
        return f"<Invoice {self.invoice_no}>"


class InvoiceItem(db.Model):
    __tablename__ = "invoice_items"
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    sno = db.Column(db.Integer, nullable=False)
    hs_code = db.Column(db.String(50), default="-")
    description = db.Column(db.String(500), nullable=False)
    qty = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(30), default="Job")
    rate = db.Column(db.Float, nullable=False, default=0.0)

    @property
    def amount(self) -> float:
        return round(self.qty * self.rate, 2)


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    method = db.Column(db.String(50), default="")
    notes = db.Column(db.String(300), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
