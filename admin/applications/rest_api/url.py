from django.urls import path, re_path
from applications.rest_api import views

app_name = "api"

urlpatterns = [
    ######################################################################
    ######################################################################
    ######################################################################    upload image
    path('upload_image', views.upload_image, name='upload_image'),
    path('delete_image', views.delete_image, name='delete_image'),
    path('get_uploaded_images', views.get_uploaded_images, name='get_uploaded_images'),


    ######################################################################
    ######################################################################
    ######################################################################    State City
    path('state/cities', views.citiesOfState),


]
