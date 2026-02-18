from app import db
from datetime import datetime, timezone

class TechnicalDebt(db.Model):
    __tablename__ = 'technical_debts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Open')
    assigned_to = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))