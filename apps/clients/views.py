from django.shortcuts import render, redirect
from django.views.generic import View, FormView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

from registration.backends.hmac.views import RegistrationView

from .forms import UserRegistrationForm, ClientEditForm


class ClientProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return redirect('auth_login')
        client = request.user.client
        return render(request, 'clients/profile.html', {'client': client})


class ClientProfileEditView(FormView):
    form_class = ClientEditForm
    template_name = 'clients/profile_edit.html'
    success_url = '../'

    def get_initial(self):
        initial_data = super(ClientProfileEditView, self).get_initial()
        client = self.request.user.client
        initial_data['full_name'] = client.full_name or ''
        initial_data['favourite_colour'] = client.favourite_colour or ''
        return initial_data

    def form_valid(self, form):
        client = self.request.user.client
        client.full_name = form.cleaned_data['full_name']
        client.favourite_colour = form.cleaned_data['favourite_colour']
        client.save()
        return super(ClientProfileEditView, self).form_valid(form)


class ClientRegistrationView(RegistrationView):
    form_class = UserRegistrationForm


# Kludge. without it render admin pages
class ClientPasswordChangeView(PasswordChangeView):
    template_name = '_registration/password_change_form.html'


class ClientPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = '_registration/password_change_done.html'


class ClientPasswordResetView(PasswordResetView):
    template_name = '_registration/password_reset_form.html'


class ClientPasswordResetDoneView(PasswordResetDoneView):
    template_name = '_registration/password_reset_done.html'


class ClientPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = '_registration/password_reset_confirm.html'


class ClientPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = '_registration/password_reset_complete.html'
