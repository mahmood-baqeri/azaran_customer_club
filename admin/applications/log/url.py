from django.urls import path, re_path
from applications.log import views

app_name = "log"
urlpatterns = [
    path('', views.index, name='index'),
    path("details/<int:id>/", views.details, name="details"),
]
