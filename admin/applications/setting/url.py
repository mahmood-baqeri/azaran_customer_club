from django.urls import path

from applications.setting.views import setting_view, slider_view

app_name = "setting"
urlpatterns = [

    path('', setting_view.index, name='index'),
    path('create', setting_view.create, name='create'),
    path('update/<int:id>', setting_view.update, name='update'),



    #######################################################################
    #######################################################################
    path('slider', slider_view.index, name='indexSlider'),
    path('slider/create', slider_view.create, name='createSlider'),
    path('slider/update/<int:id>', slider_view.update, name='updateSlider'),
    path('slider/delete/<int:id>', slider_view.delete, name='deleteSlider'),

]


