from extensions import db

class RetirementAccount(db.Model):
    __tablename__ = 'retirement_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    funds = db.Column(db.Float, default=10000.0, nullable=False)
    retirement_balance = db.Column(db.Float, default=0.0, nullable=False)
    
    user = db.relationship('User', backref=db.backref('retirement_account', uselist=False))
    
    def to_dict(self):
        return {
            "funds": self.funds,
            "401k_balance": self.retirement_balance
        }