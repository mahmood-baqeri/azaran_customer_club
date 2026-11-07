from django.urls import path, re_path
from applications.role import views

app_name = "role"
urlpatterns = [
    path('', views.index, name='index'),
    path('create', views.create, name='create'),
    path('update/<int:id>', views.update, name='update'),
    path('delete/<int:id>', views.delete, name='delete'),
]
