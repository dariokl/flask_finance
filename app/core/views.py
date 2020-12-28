from flask import render_template, flash, redirect, url_for, request, flash, jsonify, json
from app import db
from . import core
from sqlalchemy.exc import IntegrityError


from .forms import AddCompany, DeleteCompany, AddBill, DeleteBill, EditBill, Search, AddItem, DeleteItem, OrderForm

from ..models import Company, Faktura, Uplata, Article, Placement, Order
from sqlalchemy.sql import func

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
        address=form.address.data , city=form.city.data, email=form.email.data, kontakt_tel=form.kontakt_tel.data, bank_number=form.bank_number.data)
        db.session.add(new)
        db.session.commit()
        db.session.close()
        flash('Uspjesno ste dodali Firmu')
        return redirect(url_for('core.add_company'))

    if form2.submit2.data  and form2.validate_on_submit:
        delete = db.session.query(Company).filter(Company.id == form2.id.data).first()
        db.session.delete(delete)
        db.session.commit()
        db.session.close()
        flash('Uspjesno ste obrisali Firmu iz baze podataka')
        return redirect(url_for('core.add_company'))



    return render_template('addcompany.html', form=form, form2=form2, all=all)

@core.route('/editcompany/<int:id>', methods=['POST', 'GET'])
def edit_company(id):
    company = db.session.query(Company).filter(Company.id == id).first()

    form = AddCompany()

    if request.method == 'POST' and form.validate_on_submit:
        company.name = form.name.data
        company.id_number = form.id_number.data
        company.pdv_number = form.pdv_number.data
        company.address = form.address.data
        company.city = form.city.data
        company.postal = form.postal.data
        company.email = form.email.data
        company.kontakt_tel = form.kontakt_tel.data
        db.session.commit()
        db.session.close()
        flash ('Uspjesno ste promijenili podatke o firmi !')
        return redirect(url_for('core.add_company'))

    return render_template('editcompany.html', form=form, company=company)
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
        db.session.close()
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
            db.session.close()
            flash('Uspjesno ste izbrisali Fakturu')
            return redirect(url_for('core.add_bill'))
        except AttributeError:
            Faktura.query.filter_by(id=form2.id.data).delete()
            db.session.commit()
            db.session.close()
            flash('Uspjesno ste izbrisali fakturu !')
            return redirect(url_for('core.add_bill'))
    
    if form3.submit3.data and form3.validate_on_submit:
        try:
            faktura = db.session.query(Faktura).filter(Faktura.id==form3.id_edit.data).first() # Selecting the bill so i can change thec
            faktura.bill_paid = True
            faktura.billing_date = form3.date.data
            company = db.session.query(Company).filter(Company.id == faktura.company_id).first()
            company.remove_konto(faktura.bill_amount)
            new = Uplata(name=form3.type.data, billing_date=form3.date.data, amount=faktura.bill_amount, company_id=faktura.company_id, faktura_id=faktura.id, current_konto=company.konto, note=form3.note.data)
            db.session.add(new)
            db.session.commit()
            db.session.close()
            flash('Uspjesno ste izvrsili knjizenje')
            return redirect(url_for('core.add_bill'))
        except IntegrityError:
            flash ("Fakutra je vec prokiznjena")
            return redirect(url_for('core.add_bill'))

    return render_template('addbill.html', form=form, form2=form2, form3=form3, all=all)

@core.route('/racuni/<int:id>')
def bills(id):

    card = db.session.query(Company).filter(Company.id == id).first()

    return render_template('racuni.html', card=card)

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


@core.route('/additem', methods=['POST', 'GET'])
def add_item():

    all = db.session.query(Article).all()

    form = AddItem()
    form2 = DeleteItem()

    if form.submit.data and form.validate_on_submit:
        new = Article(name=form.name.data , type=form.type.data)

        db.session.add(new)
        db.session.commit()
        db.session.close()
        flash ('Uspjesno ste dodali artikal')

        return redirect(url_for('core.add_item'))

    if form2.submit2.data and form2.validate_on_submit:
        delete = db.session.query(Article).filter(Article.id == form2.id.data).first()
        db.session.delete(delete)
        db.session.commit()
        db.session.close()
        flash('Uspjesno ste obrisali artikal')

        return redirect(url_for('core.add_item'))

    return render_template('additem.html', form=form, form2=form2, all=all)


@core.route('/addorder', methods=['POST', 'GET'])
def add_order():



    return render_template('addorder.html')


@core.route('/orderhandle', methods=['POST', 'GET'])
def order_handle():

    if request.method == 'POST':
        dict = request.form.to_dict(flat=False)
 
        if dict['hitno'][0] == '1':
            new = Order(bn=dict['bn'][0], commission=dict['cn'][0], week=dict['week'][0], napomena=dict['napomena'][0], date=dict['datum'][0], hitno=True)
            db.session.add(new)
            db.session.commit()
            obj = db.session.query(Order).order_by(Order.id.desc()).first()
            id = obj.id
            f = request.form
            list = {'id': [], 'name': []}
            for key in f.keys():
                for value in f.getlist(key):
                    if 'qty' in key:
                        list['id'].append(value)
                    elif 'item' in key:
                        list['name'].append(value)

            
            for a, b in zip(list['id'], list['name']):
                place = Placement(qty=a, name=b, order_id=id)
                db.session.add(place)
                db.session.commit()
                db.session.close()
        
        else:
            new = Order(bn=dict['bn'][0], commission=dict['cn'][0], week=dict['week'][0], napomena=dict['napomena'][0], date=dict['datum'][0])
            db.session.add(new)
            db.session.commit()
            obj = db.session.query(Order).order_by(Order.id.desc()).first()
            id = obj.id
            f = request.form
            list = {'id': [], 'name': []}
            for key in f.keys():
                for value in f.getlist(key):
                    if 'qty' in key:
                        list['id'].append(value)
                    elif 'item' in key:
                        list['name'].append(value)

            
            for a, b in zip(list['id'], list['name']):
                place = Placement(qty=a, name=b, order_id=id)
                db.session.add(place)
                db.session.commit()
                db.session.close()
                    
    
    return {'message': 'ok'}


@core.route('/itemslist', methods=['POST', 'GET'])
def items_list():

    all = db.session.query(Article).all()

    data = {'results' : []}

    for item in all:
        data['results'].append({'id': item.name, 'text': item.name})

    jsonified_data = json.dumps(data)

    return jsonified_data


@core.route('/listorder', methods=['GET', 'POST'])
def list_order():

    all = db.session.query(Order).all()

    form2 = DeleteCompany()

    if form2.submit2.data and form2.validate_on_submit:
        delete = db.session.query(Order).filter(Order.id == form2.id.data).first()
        db.session.delete(delete)
        db.session.commit()
        db.session.close()
        flash ('Uspjesno ste izbrisali narudzbu')
        return redirect(url_for('core.list_order'))

    return render_template('listorder.html', all=all, form2=form2)

@core.route('/readorder/<int:id>', methods=['GET', 'POST'])
def read_order(id):

    order = db.session.query(Order).filter(Order.id == id).first()
    total = 0
    for i in order.placement:
        total += i.qty


    return render_template('orderitems.html', order=order, total=total)


@core.route('/weekly', methods=['POST', 'GET'])
def weekly():

    form = Search()

    if form.submit.data and form.validate_on_submit:
        print(form.name.data)

        return redirect(url_for('core.report', name=form.name.data))

    return render_template('searchnar.html', form=form)

@core.route('/report/<name>', methods=['POST', 'GET'])
def report(name):

    last = '2021-W' + name
    orders = db.session.query(Order).filter(Order.week == last).all()

    list = []
   
    for order in orders:
        for item in order.placement:
            list.append((item.name, item.qty))

    total = 0
    num_dict = {}
    for t in list:
        if t[0] in num_dict:
            num_dict[t[0]] = num_dict[t[0]]+t[1]
        else:
            num_dict[t[0]] = t[1]

    return render_template('weekly.html', orders=orders, num_dict=num_dict, name=name)


@core.route('/hitno', methods=['GET', 'POST'])
def hitno():

    orders = db.session.query(Order).filter(Order.hitno == True).all()

    list = []
    name = 'HITNO'
   
    for order in orders:
        for item in order.placement:
            list.append((item.name, item.qty))

    total = 0
    num_dict = {}
    for t in list:
        if t[0] in num_dict:
            num_dict[t[0]] = num_dict[t[0]]+t[1]
        else:
            num_dict[t[0]] = t[1]
    print(num_dict)

    return render_template('weekly.html', orders=orders, num_dict=num_dict, name=name)

