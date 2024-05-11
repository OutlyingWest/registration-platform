from datetime import datetime

from django.views.generic import ListView
from django.http import HttpResponse
from django.shortcuts import render


def main_view(request):
    return HttpResponse('Этот обработчик меняет пароль пользователя')


class MainView(ListView):
    template_name = 'index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['current_year'] = datetime.now().year
        return context
