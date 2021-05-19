from django.urls import path
from . import views

urlpatterns = [
    path('<str:narou_id>/', views.index, name='index'),
]