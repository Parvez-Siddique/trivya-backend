from django.urls import path
from .faqview import *

urlpatterns = [
    path('create/', FAQCreateView.as_view(), name='faq-create'),
    path('update/', FAQUpdateView.as_view(), name='faq-update'),
    path('getFAQ/', FAQUpdateView.as_view(), name='faq-get'),
    path('list/', FAQCreateView.as_view(), name='faq-list'),
    path('status-change/', FAQStatusChangeView.as_view(), name="faq-status-change"),
    path('delete/', FAQCreateView.as_view(), name="faq-delete"),
    path('faq-public-list/', FAQPublicListView.as_view(), name="faq-public-list")
]