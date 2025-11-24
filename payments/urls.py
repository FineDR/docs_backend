from django.urls import path
from . import views

urlpatterns = [
    path("initiate/", views.initiate_payment, name="initiate_payment"),  # optional
    path("checkout/", views.create_checkout, name="create_checkout"),    # required
    path("azampay/callback/", views.azampay_callback, name="azampay_callback"),  # required
    path("webhook/", views.webhook_handler, name="webhook_handler"),     # required
]
