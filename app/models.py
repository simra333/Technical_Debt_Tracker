from app import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

class TechnicalDebt(db.Model):
    __tablename__ = 'technical_debts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    risk = db.Column(db.String(50), nullable=False)
    effort_estimate = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Open')
    assigned_to = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<TechnicalDebt {self.id} - {self.title}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'risk': self.risk,
            'effort_estimate': self.effort_estimate,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat()
        }
    
class User(db.Model):
    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}>"