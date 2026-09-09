from django.urls import path
from .settingsview import *


urlpatterns = [
    path('payment-providers-list/', GetPaymentProvidersList.as_view(), name='payment-providers-list'),
    path('get-payment-config-data/', GetPaymentConfigData.as_view(), name='get-payment-config-data'),
    path('create-payment-config/', CreatePaymentConfig.as_view(), name='create-payment-config'),
    path('update-payment-config/', UpdatePaymentConfig.as_view(), name='update-payment-config')
]