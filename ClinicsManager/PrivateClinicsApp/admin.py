from os import stat_result

from flask_admin import Admin, BaseView, expose, AdminIndexView
from PrivateClinicsApp import app, db, dao
from flask_admin.contrib.sqla import ModelView
from PrivateClinicsApp.model import MedicineType, MedicalFees, BusinessRule, RegisterList, Person, Doctor, Cashier, Nurse, Ad, UserRole, Cus, MedicineUnit, Medicine, RegisterDocument, ResultDocument, MedicineBill, MedicineDetails
from flask_login import logout_user, current_user
from flask import redirect, request
import hashlib


class MyAdmin(AdminIndexView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        return self.render('admin/index.html', stats = dao.count_medicine_of_type(kw))


admin = Admin(name='Manager', app=app, template_mode='bootstrap4', index_view=MyAdmin())


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN


class MyStaffView(AuthenticatedAdmin):
    can_view_details = True
    column_list = ['firstWork', 'staff_id', 'person']


class MyCusView(AuthenticatedAdmin):
    can_view_details = True
    column_list = ['customer_id', 'person']


class MyMediCateView(AuthenticatedAdmin):
    can_view_details = True
    column_list = ['name', 'medicines']


class MyMedicineView(AuthenticatedAdmin):
    can_view_details = True
    column_list = ['name', 'amount', 'unitPrice', 'active', 'medicine_details']


class MyRegisView(AuthenticatedAdmin):
    can_view_details = True
    column_list = ['id', 'noteName', 'createDate', 'check', 'result','registerlist_id']


class MyResultView(AuthenticatedAdmin):
    can_view_details = True
    column_list = ['createDate', 'medicine_details', 'check', 'bill']


class MyMedicalFeesView(AuthenticatedAdmin):
    can_view_details = True
    column_list = ['number', ' bills']


class MyRegisterList(AuthenticatedAdmin):
    can_view_details = True
    column_list = ['id', 'date', 'nurse_id', 'registerdocuments', 'businessrule_id']


class MyRuleList(AuthenticatedAdmin):
    can_view_details = True
    column_list = ['number', 'createUpdate', 'registerlist']


class MyStatsView(AuthenticatedUser):
    @expose("/")
    def index(self):
        kw = request.args.get('kw')
        return self.render('admin/stats.html', stats=dao.count_medicine_used(kw))


class MyRevenueView(AuthenticatedUser):
    @expose("/")
    def index(self):
        kw = request.args.get('month')
        fee = MedicalFees.query.first()
        return self.render('admin/revenue.html', stats=dao.stats_revenue_by_month(kw=kw), fee=fee.number)


class LogoutView(AuthenticatedUser):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/')


admin.add_view(MyMediCateView(MedicineType, db.session))
admin.add_view(MyMediCateView(MedicineUnit, db.session))
admin.add_view(AuthenticatedAdmin(Medicine, db.session))
admin.add_view(MyCusView(Cus, db.session))
admin.add_view(MyStaffView(Nurse, db.session))
admin.add_view(MyStaffView(Ad, db.session))
admin.add_view(MyStaffView(Cashier, db.session))
admin.add_view(MyStaffView(Doctor, db.session))
admin.add_view(ModelView(Person, db.session))
admin.add_view(MyRegisView(RegisterDocument, db.session))
admin.add_view(MyResultView(ResultDocument, db.session))
admin.add_view(AuthenticatedAdmin(MedicineBill, db.session))
admin.add_view(AuthenticatedAdmin(MedicineDetails, db.session))
admin.add_view(MyRegisterList(RegisterList, db.session))
admin.add_view(ModelView(BusinessRule, db.session))
admin.add_view(ModelView(MedicalFees, db.session))
admin.add_view(MyStatsView(name='Báo cáo doanh thu thuốc'))
admin.add_view(MyRevenueView(name='Báo cáo doanh thu tháng'))
admin.add_view(LogoutView(name='Logout'))

