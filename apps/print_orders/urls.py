from django.conf.urls import url

from .views import CreatePrintOrderView, CurrentPrintOrdersView, PrintOrdersHistoryView, PrintOrderConfirmView, \
    PrintOrderEditPage, PrintOrderDetailView

urlpatterns = [
    url('^$', CurrentPrintOrdersView.as_view(), name='current_print_orders'),
    url('^create/$', CreatePrintOrderView.as_view(), name='create_print_order'),
    url('^history/$', PrintOrdersHistoryView.as_view(), name='print_orders_history'),
    url('^(?P<pk>[\d]+)/confirm/$', PrintOrderConfirmView.as_view(), name='print_orders_client_confirm'),
    url('^(?P<pk>[\d]+)/edit/$', PrintOrderEditPage.as_view(), name='print_orders_edit'),
    url('^(?P<pk>[\d]+)/$', PrintOrderDetailView.as_view(), name='print_orders_detail'),
]