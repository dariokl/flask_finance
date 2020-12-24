from flask import render_template, flash, redirect, url_for, request, flash
from app import db
from . import core


from .forms import AddCompany, DeleteCompany, AddBill, DeleteBill, EditBill, Search

from ..models import Company, Faktura, Uplata



@core.route('/', methods=['POST', 'GET'])
def home():
        
    return render_template('home.html')

@core.route('/addcompany', methods=['GET', 'POST'])
def add_company():
    """
    View is used to handle company/create/delete functions.
    """
    
    form = AddCompany()
    form2 = DeleteCompany()

    all = Company.query.all()

    

    if form.submit.data and form.validate_on_submit:
        new = Company(name=form.name.data, id_number=form.id_number.data , pdv_number=form.pdv_number.data, \
        address=form.address.data , city=form.city.data, postal=form.postal.data)
        db.session.add(new)
        db.session.commit()
        flash('Uspjesno ste dodali Firmu')
        return redirect(url_for('core.add_company'))

    if form2.submit2.data  and form2.validate_on_submit:
        Company.query.filter_by(id=form2.id.data).delete()
        db.session.commit()
        flash('Uspjesno ste obrisali Firmu iz baze podataka')
        return redirect(url_for('core.add_company'))



    return render_template('addcompany.html', form=form, form2=form2, all=all)

@core.route('/addbill', methods=['POST', 'GET'])
def add_bill():
    """
    View is used to create a bill to related comapny , and submit the value of bill inside company DUE amount wich
    is named KONTO ( column in db ) some basic remove_konto , add_konto functions are implement to sub or minus the
    amount of money based on users interaction with bill itself
    """

    form = AddBill()
    form2 = DeleteBill()
    form3 = EditBill()

    form.id_comp.choices= [(company.id , company.name)for company in Company.query.all()]

    all = Faktura.query.all()

    if form.submit.data:
        company = db.session.query(Company).filter(Company.id==form.id_comp.data).first()
        company.add_konto(form.bill_amount.data) # add an amount to konto so it can be be used in Bill query down below
        new = Faktura(bill_number=form.name.data , bill_date=form.bill_date.data, \
            bill_due=form.bill_due.data, bill_amount=form.bill_amount.data, company_id=form.id_comp.data, name=company.name, current_konto=company.konto)
        db.session.add(new)
        db.session.commit()
        flash('Uspjesno ste dodali Fakturu')

        return redirect(url_for('core.add_bill'))
    
    if form2.submit2.data  and form2.validate_on_submit:
        try:
            deleting = Faktura.query.filter_by(id=form2.id.data).first() # selecting the right bill
            remove_konto = Company.query.filter_by(id=deleting.company_id).first() # selecting company so i can manipulate due data
            remove_konto.remove_konto(deleting.bill_amount) #removing the value from konto
            Faktura.query.filter_by(id=form2.id.data).delete() 
            Uplata.query.filter_by(faktura_id = form2.id.data).delete() # Avoiding the unique constrain 
            remove_konto.reset_konto() # checking if there is no Bills on company name simply reset the DUE counter.
            db.session.commit()
            flash('Uspjesno ste izbrisali Fakturu')
            return redirect(url_for('core.add_bill'))
        except AttributeError:
            Faktura.query.filter_by(id=form2.id.data).delete()
            db.session.commit()
            flash('Uspjesno ste izbrisali fakturu !')
            return redirect(url_for('core.add_bill'))
    
    if form3.submit3.data and form3.validate_on_submit:

        faktura = db.session.query(Faktura).filter(Faktura.id==form3.id_edit.data).first()
        faktura.bill_paid = True
        faktura.billing_date = form3.date.data
        company = db.session.query(Company).filter(Company.id == faktura.company_id).first()
        company.remove_konto(faktura.bill_amount)
        new = Uplata(name=form3.type.data, billing_date=form3.date.data, amount=faktura.bill_amount, company_id=faktura.company_id, faktura_id=faktura.id, current_konto=company.konto, note=form3.note.data)
        db.session.add(new)
        db.session.commit()
        flash('Uspjesno ste izvrsili knjizenje')
        return redirect(url_for('core.add_bill'))

    return render_template('addbill.html', form=form, form2=form2, form3=form3, all=all)


@core.route('/cards/<name>', methods=['POST', 'GET'])
def cards(name):
    
    card = db.session.query(Company).filter(Company.name == name).first()
    c = db.session.query(Faktura).filter(Faktura.company_id== card.id).all()

    return render_template('cards.html', card=card, c=c)

@core.route('/searchkuf', methods=['POST', 'GET'])
def search_kuf():

    form = Search()
    if request.method == "POST" and form.validate_on_submit:

        return redirect(url_for('core.cards', name=form.name.data))

    return render_template('searchkuf.html', form=form)

@core.route('/racuni/<int:id>')
def bills(id):

    card = db.session.query(Company).filter(Company.id == id).first()

    return render_template('racuni.html', card=card)


