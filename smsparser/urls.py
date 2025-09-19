from django.urls import path
from .views import ParseSMSView

urlpatterns = [
    path('parse-sms/', ParseSMSView.as_view(), name='parse_sms'),
]
