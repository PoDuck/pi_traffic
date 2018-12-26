from django.urls import path
from . import views


app_name = 'switches'

urlpatterns = [
    path('', views.SwitchIndex.as_view(), name='index'),
    path('create', views.SwitchCreate.as_view(), name='create'),
    path('update/<int:pk>', views.SwitchUpdate.as_view(), name='update'),
    path('delete/<int:pk>', views.SwitchDelete.as_view(), name='delete'),
]
