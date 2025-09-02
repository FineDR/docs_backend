from django.urls import path
from .views import (
    CreateExportOrder,
    InitiatePayment,
    OrderStatus,
    PaymentWebhook,
    CheckPaidOrder,
)

urlpatterns = [
    path('orders/export/', CreateExportOrder.as_view(), name='create-export-order'),
    path('payments/initiate/', InitiatePayment.as_view(), name='initiate-payment'),
    path('orders/<str:order_id>/status/', OrderStatus.as_view(), name='order-status'),
    path('payments/webhook/', PaymentWebhook.as_view(), name='payment-webhook'),
    path('orders/<str:cv_id>/check/', CheckPaidOrder.as_view(), name='check-paid-order'),
]
