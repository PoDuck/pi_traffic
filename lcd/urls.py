from django.urls import path
from . import views


app_name = 'lcd'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('create', views.LcdCreate.as_view(), name='create'),
    path('update/<int:pk>', views.LcdUpdate.as_view(), name='update'),
    path('delete/<int:pk>', views.LcdDelete.as_view(), name='delete'),
]
