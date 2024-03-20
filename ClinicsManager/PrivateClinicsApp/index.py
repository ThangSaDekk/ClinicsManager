from PrivateClinicsApp import app, dao, login, db
from flask_login import current_user, login_user, logout_user
from PrivateClinicsApp.model import MedicineType, Sex, MedicalFees, BusinessRule, RegisterList, Person, Doctor, Cashier, \
    Nurse, Ad, UserRole, Cus, MedicineUnit, Medicine, RegisterDocument, ResultDocument, MedicineBill, MedicineDetails
from flask import render_template, request, redirect, flash, session, jsonify
import utils
from datetime import date, timedelta


@app.route('/payment')
def payment():
    return render_template('payment.html', UserRole=UserRole, fee=0)


@app.route('/')
def index():
    fee = MedicalFees.query.first()
    tomorrow = date.today() + timedelta(days=1)
    return render_template('index.html', UserRole=UserRole, fee=fee.number, tomorrow=tomorrow)


@app.route("/login")
def signup():
    return render_template('login.html')


@app.route("/signin")
def signin():
    return render_template('signin.html')


@app.route("/register_list")
def register_list():
    fee = MedicalFees.query.first()
    tomorrow = date.today() + timedelta(days=1)
    kw = request.args.get('kw')
    day = request.args.get('day')
    register_doc = dao.get_register(kw, day)
    return render_template('register_list.html', UserRole=UserRole, fee=fee.number, tomorrow=tomorrow,
                           register_doc=register_doc)


@app.route("/result_list")
def result_list():
    # day = date.today()  đúng là lấy ngày hôm nay nhưng do demo nên phải lấy ngày mai :v
    day = date.today()  # để test dô demo nhớ chỉnh lại :v
    kw = request.args.get('kw')
    register_doc = dao.get_register(kw=kw, day=day)
    mw = request.args.get('mw')
    cat = request.args.get('cat')
    medicine = dao.get_medicine(mw=mw, cat=cat)
    return render_template("result_list.html", UserRole=UserRole, fee=0, date=day, register_doc=register_doc,
                           medicine=medicine)


@app.route("/result_list_details")
def result_list_details():
    kw = request.args.get('kw')
    day = request.args.get('day')
    result = dao.get_result(kw, day)
    return render_template("result_list_details.html", UserRole=UserRole, fee=0, result=result)


@app.route("/bill", methods=['GET'])
def bill():
    toTotal = request.args.get('toTotal')
    fromTotal = request.args.get('fromTotal')
    toDate = request.args.get('toDate')
    fromDate = request.args.get('fromDate')
    hoadon = dao.get_bill(fromTotal, toTotal, fromDate, toDate)
    return render_template('bill.html', UserRole=UserRole, fee=0, hoadon=hoadon)


@app.route('/login/signup', methods=['POST'])
def login_signup():
    email = request.form.get('email')
    password = request.form.get('password')

    user = dao.auth_user(email=email, password=password)
    if user:
        login_user(user)
        if current_user.role == UserRole.ADMIN:
            return redirect('/admin')
        else:
            return redirect('/')

    return redirect('/login')


@app.route('/login/signin', methods=['POST'])
def login_signin():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        email = request.form['email']
        sex = request.form['sex']
        if sex == 'MALE':
            sex = Sex.MALE
        else:
            sex = Sex.FEMALE
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        # Kiểm tra xác thực mật khẩu
        if password != confirm_password:
            flash('Password and Confirm Password must match')
            return redirect('/signin')

        # Kiểm tra email đã được sử dụng chưa
        existing_user = Person.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already in use. Please choose a different one.')
            return redirect('/signin')

        # Kiểm tra số điện thoại đã được sử dụng chưa
        existing_phone = Person.query.filter_by(phoneNumber=phone).first()
        if existing_phone:
            flash('Phone number is already in use. Please choose a different one.')
            return redirect('/signin')

        # Tạo người dùng mới
        user_id = Cus(customer_id=phone)
        db.session.add(user_id)
        db.session.commit()
        new_user = Person(name=name, phoneNumber=phone, address=address,
                          email=email, sex=sex, password=password, role=UserRole.CUSTOMER, cus_id=user_id.id)

        # Thêm người dùng mới vào cơ sở dữ liệu
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'error')
        return redirect('/login')
    return redirect('/signin')


@app.route("/register", methods=['GET'])
def register():
    if request.method == 'GET':
        registerDate = request.args.get('registerDate')
        noteName = current_user.name
        if registerDate == "":
            flash('Vui lòng chọn ngày ')
            return redirect("/")
        count = RegisterDocument.query.filter(RegisterDocument.createDate == registerDate).count()
        rule = BusinessRule.query.first()
        duplicate_records = db.session.query(RegisterDocument).filter_by(noteName=noteName,
                                                                         createDate=registerDate).first()
        if duplicate_records:
            flash('Bạn đã đăng ký cho ngày đó rồi !!')
            return redirect("/")
        if count >= rule.number:
            flash('Số lượng bệnh nhân ngày bạn đăng ký đã đạt số lượng tối đa')
            return redirect("/")
        register_doc = RegisterDocument(noteName=noteName, createDate=registerDate, customer_id=current_user.cus_id)
        db.session.add(register_doc)
        db.session.commit()
        flash('Đã đăng ký thành công !!')
    return redirect("/")


@app.route("/process_register", methods=['GET'])
def process_register_list():
    if request.method == 'GET':
        day = request.args.get('registerDate')
        if day == "":
            flash('Vui lòng chọn ngày ')
            return redirect("/register_list")
        register = db.session.query(RegisterDocument).filter_by(createDate=day, registerlist_id=None)
        count = register.count()
        check_list = db.session.query(RegisterList).filter_by(date=day).first()
        if count == 0 and not check_list:
            flash('Hiện không có bệnh nhân đăng ký ngày này')
            return redirect('/register_list')
        if not check_list:
            rule = BusinessRule.query.first()
            register_list = RegisterList(date=day, nurse_id=current_user.nurse_id, businessrule_id=rule.id)
            db.session.add(register_list)
            db.session.commit()
        if count == 0:
            flash('Không có bệnh nhân nào để thêm vào danh sách')
            return redirect("/register_list")
        check_list2 = db.session.query(RegisterList).filter_by(date=day).first()
        for c in register:
            c.registerlist_id = check_list2.id
        db.session.commit()
        flash('Đã thêm tất cả bệnh nhân ngày này vào danh sách')
        return redirect("/register_list")
    return redirect("/register_list")


@app.route('/api/cart', methods=['post'])
def add_to_cart():
    data = request.json

    cart = session.get('cart')
    if cart is None:
        cart = {}

    id = str(data.get("id"))
    if id in cart:  # da co trong gio
        cart[id]['quantity'] += 1
    else:  # chua co trong gio
        cart[id] = {
            "id": id,
            "name": data.get('name'),
            "price": data.get('price'),
            "quantity": 1
        }

    session['cart'] = cart
    """
    {
        "1": {
            "id": "1",
            "name": "abc",
            "price": 123,
            "quantity": 2
        }, "2": {
            "id": "2",
            "name": "abc",
            "price": 123,
            "quantity": 1
        }
    }
    """

    return jsonify(utils.count_cart(cart))


@app.route('/api/cart/<product_id>', methods=['put'])
def update_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        quantity = request.json.get('quantity')
        cart[product_id]['quantity'] = int(quantity)

    session['cart'] = cart
    return jsonify(utils.count_cart(cart))


@app.route('/api/cart/<product_id>', methods=['delete'])
def delete_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        del cart[product_id]

    session['cart'] = cart
    return jsonify(utils.count_cart(cart))


@app.route("/api/pay", methods=['get'])
def save():
    name = request.args.get('name')
    symptom = request.args.get('symptom')
    guess = request.args.get('guess')
    register_id = request.args.get('register_id')
    if not name or not register_id or not symptom or not guess:
        flash('Yêu cầu nhập đầy đủ thông tin')
        return redirect("/result_list")
    if dao.add_receipt(session.get('cart'), name, symptom, guess, register_id):
        del session['cart']
        flash('Lưu thành công')
        return redirect("/result_list")
    else:
        flash('Lưu không thành công')
        return redirect("/result_list")


@app.route('/process_form', methods=['POST'])
def process_form():
    result_id = request.form.get('maPhieu')
    noteName = request.form.get('Ten')

    if result_id and noteName:
        medicine_detail = MedicineDetails.query.filter(MedicineDetails.result_id.__eq__(result_id)).all()
        total = 0
        fee = MedicalFees.query.first()
        for c in medicine_detail:
            total = total + (c.quantity * c.price)
        bill = MedicineBill(noteName=noteName, total=total + fee.number, fee_id=fee.id, result_id=result_id,
                            cashier_id=current_user.cashier_id)
        db.session.add(bill)
        change = ResultDocument.query.filter(ResultDocument.id.__eq__(result_id)).first()
        change.check = True
        db.session.commit()
        msg = "Đã lưu hóa đơn"
        return render_template('arlet.html', msg=msg)
    else:
        msg = "Vui lòng nhập đầy đủ thông tin"
        return render_template('arlet.html', msg=msg)



@app.context_processor
def common_responses():
    return {
        'cart_stats': utils.count_cart(session.get('cart'))
    }


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/logout")
def logout():
    if load_user:
        logout_user()
    return redirect('/')


if __name__ == '__main__':
    from PrivateClinicsApp import admin

    app.run(host='0.0.0.0', debug=True)
