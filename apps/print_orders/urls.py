from django.conf.urls import url

from .views import CreatePrintOrderView, CurrentPrintOrdersView, PrintOrdersHistoryView, PrintOrderConfirm

urlpatterns = [
    url('^$', CurrentPrintOrdersView.as_view(), name='current_print_orders'),
    url('^create/$', CreatePrintOrderView.as_view(), name='create_print_order'),
    url('^history/$', PrintOrdersHistoryView.as_view(), name='print_orders_history_view'),
    url('^(?P<pk>[\d]+)/confirm/$', PrintOrderConfirm.as_view(), name='print_orders_client_confirm'),
]