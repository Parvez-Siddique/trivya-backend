from django.urls import include, path


urlpatterns = [
    path('users/', include('trivyaserver.user.userurl')),
    path('products/', include('trivyaserver.product.producturl')),
    path('faq/', include('trivyaserver.faq.faqurl')),
    path('settings/', include('trivyaserver.settings.settingsurl')),
    path('orders/', include('trivyaserver.orders.ordersurl'))
]