from sqlalchemy import func, extract
from sqlalchemy.orm import joinedload, aliased

from PrivateClinicsApp import app, db
from flask_login import current_user
from PrivateClinicsApp.model import MedicineType, MedicalFees, BusinessRule, RegisterList, Person, Doctor, Cashier, \
    Nurse, Ad, UserRole, Cus, MedicineUnit, Medicine, RegisterDocument, ResultDocument, MedicineBill, MedicineDetails
from typing import Type
from datetime import datetime, date


def get_register(kw=None, day=None):
    register_doc = RegisterDocument.query
    if kw:
        register_doc = register_doc.filter(RegisterDocument.noteName.contains(kw))
    if day:
        register_doc = register_doc.filter(RegisterDocument.createDate.__eq__(day))
    if current_user.role == UserRole.NURSE:
        register_doc = register_doc.filter(RegisterDocument.check.__eq__(False)).all()
    if current_user.role == UserRole.CUSTOMER:
        register_doc = (RegisterDocument.query
                        .join(Cus)
                        .join(Person)
                        .options(joinedload(RegisterDocument.cus).joinedload(Cus.person))
                        .filter(Cus.id == current_user.cus_id)
                        .all())
    if current_user.role == UserRole.DOCTOR:
        register_doc = register_doc.filter(RegisterDocument.registerlist_id.__ne__(None))
        register_doc = register_doc.filter(RegisterDocument.createDate.__ge__(date.today()))
    return register_doc


def get_result(kw=None, day=None):
    if current_user.role == UserRole.CUSTOMER:
        register_alias = aliased(RegisterDocument)
        cus_alias = aliased(Cus)
        person_alias = aliased(Person)

        # Xây dựng truy vấn
        query = (
            db.session.query(ResultDocument)
            .join(register_alias, ResultDocument.register_id == register_alias.id)
            .join(cus_alias, register_alias.customer_id == cus_alias.id)
            .join(person_alias, cus_alias.id == person_alias.cus_id)
            .filter(person_alias.id == current_user.id)
        )

        # Thêm điều kiện cho ResultDocument
        if kw:
            query = query.filter(ResultDocument.noteName.contains(kw))

        if day:
            query = query.filter(ResultDocument.createDate == day)

        return query.all()

    else:
        result = ResultDocument.query
        if kw:
            result = result.filter(ResultDocument.noteName.contains(kw))
        if day:
            result = result.filter(ResultDocument.createDate.__eq__(day))
        return result


def get_medicine(mw=None, cat=None):
    query = db.session.query(Medicine, MedicineType).join(MedicineType)
    if mw:
        query = query.filter(Medicine.name.contains(mw))
    if cat:
        query = query.filter(MedicineType.name.contains(cat))
    medicine = query.all()
    return medicine


def add_receipt(cart, name, symptom=None, guess=None, register_id=None):
    if cart:
        result = ResultDocument(noteName=name, register_id=register_id, createDate=date.today(), Symptom=symptom,
                                Guess=guess, doctor_id=current_user.doctor_id)
        db.session.add(result)
        db.session.commit()
        register = RegisterDocument.query.filter(RegisterDocument.id.__eq__(register_id)).first()
        register.check = True
        db.session.commit()
        for c in cart.values():
            d = MedicineDetails(quantity=c['quantity'], price=c['price'], result_id=result.id, medicine_id=c['id'])
            db.session.add(d)
        try:
            db.session.commit()
        except:
            RegisterDocument.query.delete(ResultDocument.id.__eq__(register_id))
            return False
        else:
            medicine = Medicine.query
            for x in cart.values():
                for y in medicine:
                    if y.id == (int(x['id'])):
                        y.amount = y.amount - x['quantity']
                        db.session.commit()
            return True


def get_bill(fromTotal=None, toTotal=None, fromDate=None, toDate=None):
    bill = MedicineBill.query
    if fromTotal:
        bill = bill.filter(MedicineBill.total.__ge__(fromTotal))
    if toTotal:
        bill = bill.filter(MedicineBill.total.__le__(toTotal))
    if fromDate:
        bill = bill.filter(MedicineBill.createDate.__ge__(fromDate))
    if toDate:
        bill = bill.filter(MedicineBill.createDate.__le__(toDate))
    return bill


def get_user_by_id(user_id):
    return Person.query.get(user_id)


def auth_user(email, password):
    # password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    return Person.query.filter(Person.email.__eq__(email),
                               Person.password.__eq__(password)).first()


def count_medicine_of_type(kw=None):
    query = db.session.query(MedicineType.id, MedicineType.name, func.count(Medicine.id)) \
        .join(Medicine, Medicine.medicinetype_id.__eq__(MedicineType.id))

    if kw:
        query = query.filter(MedicineType.name.contains(kw))

    return query.group_by(MedicineType.id).all()


def count_medicine_used(kw=None):
    query = db.session.query(Medicine.id, Medicine.name, func.sum(MedicineDetails.quantity), func.sum(MedicineDetails.quantity * MedicineDetails.price)) \
        .join(MedicineDetails, MedicineDetails.medicine_id.__eq__(Medicine.id))

    if kw:
        query = query.filter(Medicine.name.contains(kw))

    return query.group_by(Medicine.id).all()


def stats_revenue_by_month(kw=None, nam=2024):
    query = db.session.query(
        extract('month', MedicineBill.createDate).label('thang'),
        func.sum(MedicineBill.total).label('tong_doanh_thu'),
        func.count(MedicineBill.id).label('so_luong_hoa_don')
    ).join(ResultDocument, MedicineBill.result_id == ResultDocument.id) \
        .filter(extract('year', MedicineBill.createDate) == nam) \
        .group_by(extract('year', MedicineBill.createDate), extract('month', MedicineBill.createDate))

    if kw:
        query = query.filter(extract('month', MedicineBill.createDate) == extract('month', kw))

    return query.all()

if __name__ == '__main__':
    with app.app_context():
        print(stats_revenue_by_month())
