from django.urls import path
from .orderview import *


urlpatterns = [
    path('create-order/', OrderCreateView.as_view(), name='create-order'),
    path('order-list/', OrderCreateView.as_view(), name='orders-list'),
    path('customer-orders/', OrderCreateView.as_view(), name='customer-orders'),
    path('my-orders/', MyOrdersListView.as_view(), name='my-orders'),
]