from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib import auth
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic.edit import CreateView

from .forms import RegisterForm


class UserLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        # TODO Email log in alert message sending will be here
        return super(UserLoginView, self).form_valid(form)

    def get_success_url(self):
        user_id = self.request.user.pk
        return reverse('account', kwargs={'user_id': user_id})


class UserRegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'register.html'

    def form_valid(self, form):
        user = form.save()
        auth.login(self.request, user)
        return redirect(self.get_success_url())

    def get_success_url(self):
        user_id = self.request.user.pk
        return reverse('account', kwargs={'user_id': user_id})


def change_password(request):
    return HttpResponse('Этот обработчик меняет пароль пользователя')


def reset_password(request):
    return HttpResponse('Этот обработчик отвечает за сброс пароля пользователя')