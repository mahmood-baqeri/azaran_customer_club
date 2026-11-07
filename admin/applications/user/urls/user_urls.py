from django.urls import path
from ..view import user_view, datatable

urlpatterns = [
    path('', user_view.index, name='user_index'),
    path('create', user_view.create, name='user_create'),
    path('update/<int:id>', user_view.update, name='user_update'),
    path('delete/<int:id>', user_view.delete, name='user_delete'),


    path('exportExcel', user_view.exportExcelUser, name='user_export_excel'),


    ######################################################################
    ######################################################################    datatabales
    path('datatable/select_users', datatable.select_users, name='user_select_users'),
    path('datatable/users', datatable.users, name='users'),

]


