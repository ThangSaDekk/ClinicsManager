from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Enum, DateTime, Date
from sqlalchemy.orm import relationship
from PrivateClinicsApp import db, app
from flask_login import UserMixin
import enum
from datetime import datetime


class Sex(enum.Enum):
    MALE = 1
    FEMALE = 2


class UserRole(enum.Enum):
    ADMIN = 1
    DOCTOR = 2
    NURSE = 3
    CASHIER = 4
    CUSTOMER = 5


class Staff(db.Model):
    __abstract__ = True
    # KhoaChinh

    id = Column(Integer, autoincrement=True, primary_key=True)

    # ThuocTinh
    staff_id = Column(String(10), unique=True, nullable=False)
    firstWork = Column(Date, default=datetime.now())
    introduce = Column(String(200), default='')

    def __str__(self):
        return self.staff_id


class Customer(db.Model):
    __abstract__ = True
    # KhoaChinh
    id = Column(Integer, autoincrement=True, primary_key=True)
    # thuoc tinh
    customer_id = Column(String(10), unique=True, nullable=False)

    def __str__(self):
        return self.customer_id


class Cus(Customer):
    registers = relationship('RegisterDocument', backref='cus', lazy=True)  # check
    person = relationship('Person', backref='cus', lazy=True, uselist=False)  # check


class Doctor(Staff):
    id = Column(Integer, autoincrement=True, primary_key=True)

    person = relationship('Person', backref='doctor', lazy=True, uselist=False)  # check
    results = relationship('ResultDocument', backref='doctor', lazy=True)  # check


class Cashier(Staff):
    id = Column(Integer, autoincrement=True, primary_key=True)

    person = relationship('Person', backref='cashier', lazy=True, uselist=False)  # check
    bills = relationship('MedicineBill', backref='cashier', lazy=True)  # check


class Nurse(Staff):
    person = relationship('Person', backref='nurse', lazy=True, uselist=False)  # check
    registerlists = relationship('RegisterList', backref='nurse', lazy=True)  # check


class Ad(Staff):
    person = relationship('Person', backref='ad', lazy=True, uselist=False)  # check


class Person(db.Model, UserMixin):
    # Thuoc tinh
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(30), nullable=False)
    birthDay = Column(Date, default=datetime.now())
    phoneNumber = Column(String(12), nullable=False, unique=True)
    address = Column(String(200))
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    sex = Column(Enum(Sex), nullable=False)
    role = Column(Enum(UserRole))

    doctor_id = Column(Integer, ForeignKey(Doctor.id))  # check
    cashier_id = Column(Integer, ForeignKey(Cashier.id))  # check
    nurse_id = Column(Integer, ForeignKey(Nurse.id))  # check
    ad_id = Column(Integer, ForeignKey(Ad.id))  # check
    cus_id = Column(Integer, ForeignKey(Cus.id))  # check

    def __str__(self):
        return self.name


class MedicineType(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    medicines = relationship('Medicine', backref='medicinetype', lazy=True)  # check

    def __str__(self):
        return self.name


class MedicineUnit(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    medicines = relationship('Medicine', backref='medicineunit', lazy=True)  # check

    def __str__(self):
        return self.name


class Medicine(db.Model):
    # khoa chinh

    id = Column(Integer, primary_key=True, autoincrement=True)

    # thuoc tinh

    name = Column(String(50), nullable=False)
    amount = Column(Integer, default=0)
    unitPrice = Column(Float, default=0)
    active = Column(Boolean, default=False)
    importDate = Column(DateTime, default=datetime.now())
    expirationDate = Column(DateTime, default=datetime.now())
    manufacturer = Column(String(100), default='')
    description = Column(String(100), default='')
    medicineunit_id = Column(Integer, ForeignKey(MedicineUnit.id), nullable=False)  # check
    medicinetype_id = Column(Integer, ForeignKey(MedicineType.id), nullable=False)  # check
    medicine_details = relationship('MedicineDetails', backref='medicine', lazy=True)  # check

    def __str__(self):
        return self.name


class BusinessRule(db.Model):
    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False)
    createUpdate = Column(Date, default=datetime.now())
    registerlist = relationship('RegisterList', backref='businessrule', lazy=True)  # check


class RegisterList(db.Model):
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    nurse_id = Column(Integer, ForeignKey(Nurse.id), nullable=False)  # check
    businessrule_id = Column(Integer, ForeignKey(BusinessRule.id))  # check
    registerdocuments = relationship('RegisterDocument', backref='registerlist', lazy=True)


class RegisterDocument(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    noteName = Column(String(50))
    customer_id = Column(Integer, ForeignKey(Cus.id), nullable=False)  # check
    registerlist_id = Column(Integer, ForeignKey(RegisterList.id))
    createDate = Column(Date, default=datetime.now())
    check = Column(Boolean, default=False)
    result = relationship('ResultDocument', backref='RegisterDocument', uselist=False, lazy=True)  # check

    def __str__(self):
        return self.noteName


class ResultDocument(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    noteName = Column(String(50))
    register_id = Column(Integer, ForeignKey(RegisterDocument.id))  # check
    createDate = Column(Date, default=datetime.now())
    Symptom = Column(String(255))
    Guess = Column(String(255))
    check = Column(Boolean, default=False)
    doctor_id = Column(Integer, ForeignKey(Doctor.id), nullable=False)  # check
    medicine_details = relationship('MedicineDetails', backref='resultdocument', lazy=True)  # check
    bill = relationship('MedicineBill', backref='resultdocument', uselist=False, lazy=True)  # check

    def __str__(self):
        return self.noteName


class MedicalFees(db.Model):
    id = Column(Integer, primary_key=True)
    number = Column(Float, nullable=False)
    createUpdate = Column(Date, default=datetime.now())

    bills = relationship('MedicineBill', backref='medicalfees', lazy=True)  # check


class MedicineBill(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    noteName = Column(String(50))
    createDate = Column(DateTime, default=datetime.now())
    total = Column(Float, nullable=False)
    check = Column(Boolean, default=False)
    fee_id = Column(Integer, ForeignKey(MedicalFees.id), nullable=False)  # check
    result_id = Column(Integer, ForeignKey(ResultDocument.id), nullable=False)  # check
    cashier_id = Column(Integer, ForeignKey(Cashier.id), nullable=True)  # check

    def __str__(self):
        return self.noteName





class MedicineDetails(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(Integer, ForeignKey(Medicine.id), nullable=False)  # check
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    use = Column(String(255))
    result_id = Column(Integer, ForeignKey(ResultDocument.id), nullable=False)  # check


if __name__ == '__main__':
    with app.app_context():
        db.create_all()


