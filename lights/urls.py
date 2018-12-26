from django.urls import path
from . import views


app_name = 'lights'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('create', views.LightCreate.as_view(), name='create'),
    path('update/<int:pk>', views.LightUpdate.as_view(), name='update'),
    path('delete/<int:pk>', views.LightDelete.as_view(), name='delete'),
]
