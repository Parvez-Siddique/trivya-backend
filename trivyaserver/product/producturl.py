from django.urls import path
from .productview import *


urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('update/', ProductUpdateView.as_view(), name='product-update'),
    path('getProduct/', ProductUpdateView.as_view(), name='product-get'),
    path('list/', ProductCreateView.as_view(), name='product-list'),
    path('status-change/', ProductStatusChangeView.as_view(), name="product-status-change"),
    path('product-delete/', ProductCreateView.as_view(), name="product-delete"),
    path('product-public-list/', ProductPublicListViewAPI.as_view(), name="product-public-list"),
    path('get-public-product-details/', GetPublicProductDetails.as_view(), name="product-public-list"),
    path('get-cart-details/', GetCartDetails.as_view(), name="get-cart-details"),
]