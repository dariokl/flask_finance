from app import db


class Company(db.Model):

    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    id_number = db.Column(db.Integer, unique=True)
    pdv_number = db.Column(db.Integer, unique=True)
    address = db.Column(db.String)
    city = db.Column(db.String)
    postal = db.Column(db.String)
    
    konto = db.Column(db.REAL, default=0)

    rel = db.relationship('Faktura', backref='dug', cascade="all, delete, delete-orphan")
    rel_u = db.relationship('Uplata', backref='uplata',cascade="all, delete, delete-orphan")


    def add_konto(self, amount):
        self.konto += amount
    
    def remove_konto(self, amount):
        self.konto -= amount
    
    def reset_konto(self):
        if len(self.rel) == 0:
            self.konto = 0.0

    
    def __repr__(self):

        return '{}'.format(self.name)


class Faktura(db.Model):

    __tablename__ = 'fakture'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    bill_number = db.Column(db.String)
    bill_date = db.Column(db.String)
    bill_due = db.Column(db.String)
    bill_amount = db.Column(db.REAL)
    bill_paid = db.Column(db.Boolean , default=False)
    billing_date = db.Column(db.String, default=None)

    current_konto = db.Column(db.REAL)

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    payment = db.relationship('Uplata', cascade="all, delete, delete-orphan")

class Uplata(db.Model):
    __tablename__ = 'uplate'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    billing_date = db.Column(db.String)
    amount = db.Column(db.REAL)
    note = db.Column(db.String)

    current_konto = db.Column(db.REAL)

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    faktura_id = db.Column(db.Integer, db.ForeignKey('fakture.id'), unique=True)



