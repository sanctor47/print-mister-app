from django.conf.urls import url

from .views import ClientProfileView, ClientPasswordChangeView, ClientPasswordChangeDoneView, ClientPasswordResetView, \
    ClientPasswordResetDoneView, ClientPasswordResetConfirmView, ClientPasswordResetCompleteView, \
    ClientRegistrationView, ClientProfileEditView

urlpatterns = [
    url(r'^profile/$', ClientProfileView.as_view(), name='client_profile'),
    url(r'^profile/edit/$', ClientProfileEditView.as_view(), name='client_profile_edit'),
    url(r'^register/$', ClientRegistrationView.as_view(), name='registration_register'),

    url(r'^password/change/$', ClientPasswordChangeView.as_view(success_url='done/'), name='auth_password_change'),
    url(r'^password/change/done/$', ClientPasswordChangeDoneView.as_view(), name='auth_password_change_done'),
    url(r'^password/reset/$', ClientPasswordResetView.as_view(
            email_template_name='clients/password_reset_email.html', success_url='/accounts/password/reset/done/',
        ), name='auth_password_reset'),
    url(r'^password/reset/done/$', ClientPasswordResetDoneView.as_view(), name='auth_password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', ClientPasswordResetConfirmView.as_view(
            success_url='/accounts/password/reset/complete/'), name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$', ClientPasswordResetCompleteView.as_view(), name='auth_password_reset_complete'),

]
