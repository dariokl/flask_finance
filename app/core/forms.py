from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, FloatField, FieldList, FormField, TextField
from wtforms.validators import DataRequired, Length
from markupsafe import Markup



class AddCompany(FlaskForm):
    name = StringField('Ime Firme')
    id_number = IntegerField('ID Broj Firme')
    pdv_number = IntegerField('PDV Broj')
    address = StringField('Adresa firme')
    city = StringField('Grad')
    bank_number = StringField('Broj Racuna')
    email = StringField('Email Adresa')
    kontakt_tel = StringField('Kontakt Tel.')
    submit = SubmitField('Dodaj')

class DeleteCompany(FlaskForm):
    id = IntegerField('ID U bazi')
    submit2 = SubmitField('Obrisi')

class AddBill(FlaskForm):
    id_comp = SelectField('Firma', choices=[()])
    name = StringField('Broj Racuna', validators=[DataRequired(message='Obavezno unijeti broj racuna')])
    bill_date = StringField('Datum Racuna', validators=[DataRequired(message='Obavezno unijeti datum racuna')])
    bill_due = StringField('Datum Valute', validators=[DataRequired(message='Obavezno unijeti datum VALUTE')])
    bill_amount = FloatField('Ukupno', validators=[DataRequired(message='Obavezno unijeti iznos Fakture/Racuna u KM')])
    submit = SubmitField('Unesi')

class DeleteBill(FlaskForm):
    id = IntegerField('ID U bazi')
    submit2 = SubmitField('Obrisi')

class EditBill(FlaskForm):
    id_edit = IntegerField('Alo')
    date = StringField('Datum Uplate', validators=[DataRequired(message='Obavezno unijeti datum uplate')])
    type = StringField('Vrsta / Osnov uplate', validators=[DataRequired(message='Unijeti Vrstu/Osnov uplate (npr. NLB BANKA)')])
    note = StringField('Napomena')
    submit3 = SubmitField('Knjizi')

class Search(FlaskForm):
    name = StringField('Search')
    submit = SubmitField('Trazi')

class AddItem(FlaskForm):
    name = StringField('Ime artikla', validators=[DataRequired()])
    type = SelectField('Vrsta Artikla', validators=[DataRequired()], choices=[('Vrata', 'Vrata'), ('Nogari', 'Nogari'), ('Pl. Stola', 'Ploce stolova')])

    submit = SubmitField('Dodaj artikal')


class DeleteItem(FlaskForm):
    id = IntegerField('Hidden')
    submit2 = SubmitField('Obrisi')

class PlacementField(FlaskForm):
    name = StringField('Ime artikla')
    qty = IntegerField('Kolicina')


class OrderForm(FlaskForm):
    bestel = StringField('Bestelnummer')
    commission = StringField('Commission Broj')
    order_week = StringField('Order Week')
    placement = FieldList(StringField())
    submit = SubmitField('Dodaj Narudzbu')