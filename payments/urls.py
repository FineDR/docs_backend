# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('payments/checkout/', views.create_checkout, name='create_checkout'),
    path('payments/azampay/callback/', views.azampay_callback, name='azampay_callback'),
]
