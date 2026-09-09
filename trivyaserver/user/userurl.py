from django.urls import path
from .userview import *

urlpatterns = [
    path('admin-login/',AdminLogin.as_view(), name="admin-login"),
    path('create-user/', UserCreateView.as_view(), name="create-user"),
    path('customer-login/', CustomerLogin.as_view(), name="customer-login"),
    path('customers-list/', UserListView.as_view(), name="customers-list"),
    path('<int:pk>/', UserUpdateView.as_view(), name='user-update'),
]