from flask import render_template, flash, redirect, url_for, request, flash, jsonify, json
from app import db
from . import core
from sqlalchemy.exc import IntegrityError

from .forms import AddCompany, DeleteCompany, AddBill, DeleteBill, EditBill, Search, AddItem, DeleteItem, OrderForm

from ..models import Company, Faktura, Uplata, Article, Placement, Order
from sqlalchemy.sql import func
from collections import OrderedDict


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
        new = Company(name=form.name.data, id_number=form.id_number.data, pdv_number=form.pdv_number.data,
                      address=form.address.data, city=form.city.data, email=form.email.data, kontakt_tel=form.kontakt_tel.data, bank_number=form.bank_number.data)
        db.session.add(new)
        db.session.commit()
        db.session.close()
        flash('Uspjesno ste dodali Firmu')
        return redirect(url_for('core.add_company'))

    if form2.submit2.data and form2.validate_on_submit:
        delete = db.session.query(Company).filter(
            Company.id == form2.id.data).first()
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
        flash('Uspjesno ste promijenili podatke o firmi !')
        return redirect(url_for('core.add_company'))

    return render_template('editcompany.html', form=form, company=company)


@core.route('/addbill', methods=['POST', 'GET'])
def add_bill():
    """
    View is used to create a bill to related comapny , and submit the value of bill inside company DUE amount wich
    is named KONTO ( column in db ) some basic remove_konto , add_konto methods are implement to sub or minus the
    amount of money based on users interaction with bill itself
    """

    form = AddBill()
    form2 = DeleteBill()
    form3 = EditBill()

    form.id_comp.choices = [(company.id, company.name)
                            for company in Company.query.all()]

    all = db.session.query(Faktura).order_by(Faktura.bill_date.desc()).all()

    if form.submit.data:
        company = db.session.query(Company).filter(
            Company.id == form.id_comp.data).first()
        # add an amount to konto so it can be be used in Bill query down below
        company.add_konto(form.bill_amount.data)
        new = Faktura(bill_number=form.name.data, bill_date=form.bill_date.data,
                      bill_due=form.bill_due.data, bill_amount=form.bill_amount.data, company_id=form.id_comp.data, name=company.name, current_konto=company.konto)
        db.session.add(new)
        db.session.commit()
        db.session.close()
        flash('Uspjesno ste dodali Fakturu')

        return redirect(url_for('core.add_bill'))

    if form2.submit2.data and form2.validate_on_submit:
        try:
            deleting = Faktura.query.filter_by(
                id=form2.id.data).first()  # selecting the right bill
            # selecting company so i can manipulate due data
            remove_konto = Company.query.filter_by(
                id=deleting.company_id).first()
            # removing the value from konto
            remove_konto.remove_konto(deleting.bill_amount)
            Faktura.query.filter_by(id=form2.id.data).delete()
            # Avoiding the unique constrain
            Uplata.query.filter_by(faktura_id=form2.id.data).delete()
            # checking if there is no Bills on company name simply reset the DUE counter.
            remove_konto.reset_konto()
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
            # Selecting the bill so i can change thec
            faktura = db.session.query(Faktura).filter(
                Faktura.id == form3.id_edit.data).first()
            faktura.bill_paid = True
            faktura.billing_date = form3.date.data
            company = db.session.query(Company).filter(
                Company.id == faktura.company_id).first()
            company.remove_konto(faktura.bill_amount)
            new = Uplata(name=form3.type.data, billing_date=form3.date.data, amount=faktura.bill_amount,
                         company_id=faktura.company_id, faktura_id=faktura.id, current_konto=company.konto, note=form3.note.data)
            db.session.add(new)
            db.session.commit()
            db.session.close()
            flash('Uspjesno ste izvrsili knjizenje')
            return redirect(url_for('core.add_bill'))
        except IntegrityError:
            flash("Fakutra je vec prokiznjena")
            return redirect(url_for('core.add_bill'))

    return render_template('addbill.html', form=form, form2=form2, form3=form3, all=all)


@core.route('/racuni/<int:id>')
def bills(id):
    """Search each bill whith the id """

    card = db.session.query(Company).filter(Company.id == id).first()

    return render_template('racuni.html', card=card)


@core.route('/cards/<name>', methods=['POST', 'GET'])
def cards(name):

    card = db.session.query(Company).filter(Company.name == name).first()
    c = db.session.query(Faktura).filter(Faktura.company_id == card.id).all()

    return render_template('cards.html', card=card, c=c)


@core.route('/searchkuf', methods=['POST', 'GET'])
def search_kuf():

    form = Search()
    if request.method == "POST" and form.validate_on_submit:

        return redirect(url_for('core.cards', name=form.name.data))

    return render_template('searchkuf.html', form=form)


@core.route('/additem', methods=['POST', 'GET'])
def add_item():
    """
     BASIC CRUD 
    """

    all = db.session.query(Article).all()

    form = AddItem()
    form2 = DeleteItem()

    if form.submit.data and form.validate_on_submit:
        new = Article(name=form.name.data, type=form.type.data)

        db.session.add(new)
        db.session.commit()
        db.session.close()
        flash('Uspjesno ste dodali artikal')

        return redirect(url_for('core.add_item'))

    if form2.submit2.data and form2.validate_on_submit:
        delete = db.session.query(Article).filter(
            Article.id == form2.id.data).first()
        db.session.delete(delete)
        db.session.commit()
        db.session.close()
        flash('Uspjesno ste obrisali artikal')

        return redirect(url_for('core.add_item'))

    return render_template('additem.html', form=form, form2=form2, all=all)

@core.route('/edititem/<int:id>', methods=['POST', 'GET'])
def edit_item(id):

    form = AddItem()

    item = db.session.query(Article).filter(Article.id == id).first()

    if form.submit.data and form.validate_on_submit:
        item.name = form.name.data
        item.type = form.type.data
        db.session.commit()
        db.session.close()
        flash ('Uspjesno ste iznajmili artikal')

        return redirect(url_for('core.add_item'))

    return render_template('edititem.html', form=form, item=item)
@core.route('/addorder', methods=['POST', 'GET'])
def add_order():

    return render_template('addorder.html')


@core.route('/orderhandle', methods=['POST', 'GET'])
def order_handle():
    """
    This view is responsible for storing all the order data , ajax does the form submision after that there is one simple check
    that is related to nature of bussiness , checking out is the order "Important" if it is it just enables a boolean column in table ,
    later on this boolean is used for order filtering
    """

    if request.method == 'POST':
        dict = request.form.to_dict(flat=False)

        if dict['hitno'][0] == '1':
            new = Order(bn=dict['bn'][0], commission=dict['cn'][0], week=dict['week']
                        [0], napomena=dict['napomena'][0], date=dict['datum'][0], hitno=True)
            db.session.add(new)
            db.session.commit()
            # The only possible complication could be related to multiple users trying to store an order
            # Because we save the order first and then use the last saved id to create relationship with ordered items
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

            # Simple for loop handling the incoming form data .
            for a, b in zip(list['id'], list['name']):
                place = Placement(qty=a, name=b, order_id=id)
                db.session.add(place)
                db.session.commit()
                db.session.close()

        else:

            new = Order(bn=dict['bn'][0], commission=dict['cn'][0], week=dict['week']
                        [0], napomena=dict['napomena'][0], date=dict['datum'][0])
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
    """
    Required to make Select 2 lib work 
    """

    all = db.session.query(Article).all()

    data = {'results': []}

    for item in all:
        data['results'].append({'id': item.name, 'text': item.name})

    jsonified_data = json.dumps(data)

    return jsonified_data


@core.route('/listorder', methods=['GET', 'POST'])
def list_order():

    all = db.session.query(Order).order_by(Order.week.desc()).all()

    form2 = DeleteCompany()

    if form2.submit2.data and form2.validate_on_submit:
        delete = db.session.query(Order).filter(
            Order.id == form2.id.data).first()
        db.session.delete(delete)
        db.session.commit()
        db.session.close()
        flash('Uspjesno ste izbrisali narudzbu')
        return redirect(url_for('core.list_order'))

    return render_template('listorder.html', all=all, form2=form2)


@core.route('/readorder/<int:id>', methods=['GET', 'POST'])
def read_order(id):
    """
    Single order view, i will consider adding "Total" column in database later on 
    """

    order = db.session.query(Order).filter(Order.id == id).first()
    total = 0
    for i in order.placement:
        total += i.qty

    return render_template('orderitems.html', order=order, total=total)


@core.route('/weekly', methods=['POST', 'GET'])
def weekly():

    form = Search()

    if form.submit.data and form.validate_on_submit:

        return redirect(url_for('core.report', name=form.name.data))

    return render_template('searchnar.html', form=form)


@core.route('/report/<name>', methods=['POST', 'GET'])
def report(name):
    """
    Search mechanism for all orders according to selected week , the things get little bit coplicated up on displaying whole list of 
    ordered items and the exact qty more explanation in two of loops down below 
    """

    last = '2021-W' + name
    orders = db.session.query(Order).filter(Order.week == last).all()

    list = []

    # Creating a tuple for each item and its quantity
    for order in orders:
        for item in order.placement:
            list.append((item.name, item.qty))

    # Looping over tuple and creating a dictionary where the keys are item name and value is add up everything time the
    # Item name is the same...
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

    num_dict = {}
    for t in list:
        if t[0] in num_dict:
            num_dict[t[0]] = num_dict[t[0]]+t[1]
        else:
            num_dict[t[0]] = t[1]


    return render_template('weekly.html', orders=orders, num_dict=num_dict, name=name)

@core.route('/material/<name>', methods=['GET', 'POST'])
def material(name):
    """ 
    A huge view , designet to get material list for each doors that have to be crafted , 
    in order to make the whole production process faster. Worker could just search for a week
    of shipment and he could see all the material required for all the orders from that week.
    Honestly i could have create another table to handle all the material registration , right now
    im just coding super fast and i need solution ASAP , in future this could be converted to table to 
    minimize amount of code 
    """
    material = {
        #Uredu
        "D4 2559 x 920": [
            {
            '40x20x2559mm': (2559, 2),
             '40x20x880mm': (880, 1),
             '40x60x880mm': (880, 1),
             'F40x5x880mm': (880, 3),
             '15x15x879mm': (879, 16),
             '15x15x615mm': (615, 16),
             'Staklo 872x608': (0, 4)
             }
             ],
        #Uredu
        "D4 2559 x 820": [
            {
                '40x20x2559mm': (2559, 2),
                '40x20x780mm': (780, 1),
                '40x60x780mm': (780, 1),
                'F40x5x780mm': (780, 3),
                '15x15x779mm': (779, 16),
                '15x15x615mm': (615, 16),
                'Staklo 772x608': (0, 4)
            }
        ],
        #Uredu
        "D4 2294 x 920": [
            {'40x20x2294mm': (2294, 2),
             '40x20x880mm': (880, 1),
             '40x60x880mm': (880, 1),
             'F40x5x880mm': (880, 3),
             '15x15x879mm': (879, 16),
             '15x15x549mm': (549, 16),
             'Staklo 872x542': (0, 4)

             }
             ],
        #Uredu
        "D4 2294 x 820":
        [
            {
            '40x20x2294mm': (2294, 2),
             '40x20x780mm': (780, 1),
             '40x60x780mm': (780, 1),
             'F40x5x780mm': (780, 3),
             '15x15x779mm': (779, 16),
             '15x15x549mm': (549, 16),
             'Staklo 772x542': (0, 4)

             }
        ],
        #Uredu
        'D3 2294 x 920': [
            {
                '40x20x2294mm': (2994, 2),
                '40x20x880mm': (880, 1),
                '40x60x880mm': (880, 1),
                'F40x5x880mm': (880, 2),
                '15x15x879mm': (879, 12),
                '15x15x733.5mm': (733.5, 12),
                'Staklo 872x727': (0, 3)
            }
        ],
        #Uredu
        'D3 2559 x 920': [
            {
                '40x20x2559mm': (2559, 2),
                '40x20x880mm': (880, 1),
                '40x60x880mm': (880, 1),
                'F40x5x880mm': (880, 2),
                '15x15x879mm': (879, 12),
                '15x15x822mm': (822, 12),
                'Staklo 872x815': (0, 3)
            }
        ],
        #Uredu
        'D3 2559 x 820': [
            {
                '40x20x2559mm': (2559, 2),
                '40x20x780mm': (780, 1),
                '40x60x780mm': (780, 1),
                'F40x5x780mm': (780, 2),
                '15x15x779mm': (779, 12),
                '15x15x822mm': (822, 12),
                'Staklo 727x815': (0, 3)
            }
        ],
        #Uredu
        'D3 2294 x 820': [
            {
                '40x20x2294mm': (2294, 2),
                '40x20x780mm': (780, 1),
                '40x60x780mm': (780, 1),
                'F40x5x780mm': (780, 2),
                '15x15x779mm': (779, 12),
                '15x15x734mm': (734, 12),
                'Staklo 772x727': (0, 3)
            }
        ],
        #Uredu
        'DK 2559 x 820' : [
            {
                '40x20x2559mm': (2559, 2),
                '40x20x780mm': (780, 1),
                '40x60x780mm': (780, 1),
                'F40x5x2479mm': (2479, 1),
                'F40x5x185mm': (185, 1),
                'F40x5x580mm': (580, 1),
                '15x15x194mm': (194, 8),
                '15x15x822mm': (822, 8),
                '15x15x579mm': (579, 8),
                '15x15x1650mm': (1650, 8),
                'Staklo 187x816': (0, 1),
                'Staklo 187x1642': (0,1),
                'Staklo 572x1642': (0, 1),
                'Staklo 572x816': (0, 1)
            }
        ],
        #Uredu
        "DK 2559 x 920": [
            {
                '40x20x2559mm': (2559, 2),
                '40x20x880mm': (880, 1),
                '40x60x880mm': (880, 1),
                'F40x5x2479mm': (2479, 1),
                'F40x5x655mm': (655, 1),
                'F40x5x220mm': (220, 1),
                '15x15x219mm': (219, 8),
                '15x15x654mm': (654, 8),
                '15x15x822mm': (822, 8),
                '15x15x1650mm': (1650, 8),
                'Staklo 647x816': (0, 1),
                'Staklo 212x816': (0, 1),
                'Staklo 647x1642': (0, 1),
                'Staklo 212x1642': (0, 1)
            }
        ],
        #Uredu
        "DK 2294 x 820": [
            {
                '40x20x2294mm': (2294, 2),
                '40x20x780mm': (780, 1),
                '40x60x780mm': (780, 1),
                'F40x5x2214mm': (2214, 1),
                'F40x5x195mm': (195, 1),
                'F40x5x580mm': (580, 1),
                '15x15x194mm': (194, 8),
                '15x15x735mm': (735, 8),
                '15x15x1473mm': (1473, 8),
                '15x15x579mm': (579, 8),
                'Staklo 187x728': (0, 1),
                'Staklo 572x728': (0, 1),
                'Staklo 187x1465': (0, 1),
                'Staklo 572x1465': (0, 1)
            }
        ],
        #Uredu
        'DK 2294 x 920': [
            {
                '40x20x2294mm': (2294, 2),
                '40x20x880mm': (880, 1),
                '40x60x880mm': (880, 1),
                'F40x5x2214mm': (2214, 1),
                'F40x5x655mm': (655, 1),
                'F40x5x220mm': (220, 1),
                '15x15x219mm': (219, 8),
                '15x15x654mm': (654, 8),
                '15x15x734mm': (734, 8),
                '15x15x1473mm': (1473, 8),
                'Staklo 647x728': (0, 1),
                'Staklo 212x728': (0, 1),
                'Staklo 647x1465': (0, 1),
                'Staklo 212x1465': (0, 1)
            }
        ],
        #Uredu
        'P3 2575 x 915': [
            {
                '40x20x2575mm': (2575, 1),
                '40x20x2479mm': (2479, 1),
                'F40x5x875mm': (875, 2),
                '15x15x874mm': (874, 12),
                '15x15x822mm': (822, 12),
                'Staklo 867x815': (0, 3)

            }
        ],
        #Uredu
        'P3 2575 x 455': [
            {
                '40x20x2575mm': (2575, 1),
                '40x20x2479mm': (2479, 1),
                'F40x5x415mm': (415, 2),
                '15x15x414mm': (414, 12),
                '15x15x822mm': (822, 12),
                'Staklo 407x815': (0, 3)
            }
        ],
        #Uredu
        'P3 2310 x 915': [
            {
                '40x20x2310mm': (2310, 1),
                '40x20x2214mm': (2214, 1),
                'F40x5x875mm': (875, 2),
                '15x15x874mm': (874, 12),
                '15x15x733.5mm': (733.5, 12),
                'Staklo 867x727': (0, 3)
            }
        ],
        #Uredu
        'P3 2310 X 455': [
            {
                '40x20x2310mm': (2130, 1),
                '40x20x2214mm': (2214, 1),
                'F40x5x415mm': (415, 2),
                '15x15x414mm': (414, 12),
                '15x15x733.5mm': (733.5, 12),
                'Staklo 407x727': (0, 3)
            }
        ],
        #Uredu
        'P4 2310 x 455': [
            {
                '40x20x2310mm': (2310, 1),
                '40x20x2214mm': (2214, 1),
                'F40x5x415mm': (415, 3),
                '15x15x414mm': (414, 16),
                '15x15x549mm': (549, 16),
                'Staklo 407x542': (0, 4)
            }
        ],
        #Uredu
        'P4 2310 x 915': [
            {
                '40x20x2310mm': (2310, 1),
                '40x20x2214mm': (2214, 1),
                'F40x5x875mm': (875, 3),
                '15x15x874mm': (874, 16),
                '15x15x549mm': (549, 16),
                'Staklo 867x542': (0, 4)
            }
        ],
        #Uredu
        'P4 2575 x 915': [
            {
                '40x20x2575mm': (2575, 1),
                '40x20x2479mm': (2479, 1),
                'F40x5x875mm': (875, 3),
                '15x15x874mm': (874, 16),
                '15x15x615mm': (615, 16),
                'Staklo 867x608': (0, 4)
            }
        ],
        #Uredu
        'P4 2575 x 455': [
            {
                '40x20x2575mm': (2575, 1),
                '40x20x2479mm': (2479, 1),
                'F40x5x415mm': (415, 3),
                '15x15x414mm': (414, 16),
                '15x15x615mm': (615, 16),
                'Staklo 407x608': (0, 4),
            }
        ],
        #Uredu
        'PK 2575 x 455': [
            {
                '40x20x2575mm': (2575, 1),
                '40x20x2479mm': (2479, 1),
                'F40x5x415mm': (415, 1),
                '15x15x414mm': (414, 8),
                '15x15x822mm': (822, 4),
                '15x15x1650mm': (1650, 4),
                'Staklo 407x815': (0, 1),
                'Staklo 407x1643': (0, 1),
            }
        ],
        #Uredu
        'PK 2575 x 915': [
            {
                '40x20x2575mm': (2575, 1),
                '40x20x2479mm': (2479, 1),
                'F40x5x875mm': (875, 1),
                '15x15x822mm': (822, 4),
                '15x15x1650mm': (1650, 4),
                '15x15x874mm': (874, 8),
                'Staklo 867x815': (0, 1),
                'Staklo 867x1643': (0, 1)
            }
        ],
        #Uredu
        'PK 2310 x 915': [
            {
                '40x20x2310mm': (2130, 1),
                '40x20x2214mm': (2214, 1),
                'F40x5x875mm': (875, 1),
                '15x15x874mm': (874, 8),
                '15x15x734mm': (734, 4),
                '15x15x1473mm': (1473, 4),
                'Staklo 867x728': (0, 1),
                'Staklo 867x1465': (0, 1)
            }
        ],
        #Uredu
        'PK 2130 x 455': [
            {
                '40x20x2130mm': (2310, 1),
                '40x20x2214mm': (2214, 1),
                'F40x5x415mm': (415, 1),
                '15x15x414mm': (414, 8),
                '15x15x734mm': (734, 4),
                '15x15x1472mm': (1472, 4),
                'Staklo 407x728': (0, 1),
                'Staklo 407x1465': (0, 1)
            }
        ]
    
    }

    last = '2021-W' + name
    orders = db.session.query(Order).filter(Order.week == last).all()
    list= []
    for order in orders:
        for item in order.placement:
            list.append((item.name, item.qty))


    num_dict = {}
    for t in list:
       
        if t[0] in num_dict:
            num_dict[t[0]] = num_dict[t[0]]+t[1]
        else:
            num_dict[t[0]] = t[1]
        


    a = [(material[key], num_dict[key])for key in num_dict.keys() if key in material]
    final_list = []

 
    for i in a:
        for k, v in i[0][0].items():
            final_list.append((k, v[1] * i[1], (v[0] * i[1] / 100)))
    

    material_dict = {}

    print(final_list)
    for t in final_list:
        if t[0] in material_dict.keys():
         material_dict[t[0]][0] += t[1]
         material_dict[t[0]][1] += t[2]

             
          
        elif t[0] not in material_dict.keys():
            material_dict[t[0]] = [t[1], t[2]]
    
 
    print(material_dict)
   
    
    list_15 = []
    list_4020 = []
    list_4060 = []
    list_f = []
    dict1 = OrderedDict(sorted(material_dict.items()))
    for k,v in dict1.items():
        if '15x15' in k:
            list_15.append(v[1])
        elif '40x20' in k:
            list_4020.append(v[1])
        elif '40x60' in k:
            list_4060.append(v[1])
        elif 'F40x5' in k:
            list_f.append(v[1])
    


    return render_template('material.html', orders=orders, name=name, material_dict=dict1, list_15=sum(list_15), list_4020=sum(list_4020),list_4060=sum(list_4060), list_f=sum(list_f))

@core.route('/materialsrc', methods=['GET', 'POST'])
def material_search():

    form = Search()

    if form.submit.data and form.validate_on_submit:
        return redirect(url_for('core.material', name=form.name.data))
    
    return render_template('searchmat.html', form=form)

