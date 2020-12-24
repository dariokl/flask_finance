from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, Length
from markupsafe import Markup



class AddCompany(FlaskForm):
    name = StringField('Ime Firme', validators=[DataRequired(message='Obavezan unos imena Firme')])
    id_number = IntegerField('ID Broj Firme', validators=[DataRequired(message='Obavezan ID broj Firme'), Length(min=13, message='ID Broj mora imati 13 cifri')])
    pdv_number = IntegerField('PDV Broj', validators=[DataRequired(message='Obavezan PDV broj Firme'), Length(min=12, message='PDV broj mora imati 12 cifri')])
    address = StringField('Adresa firme')
    city = StringField('Grad')
    postal = IntegerField('Postanski Broj')
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

