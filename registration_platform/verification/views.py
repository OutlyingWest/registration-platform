from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from .forms import UserDocumentsFormSet, UserProfileForm
from .models import UserDocument


class UserAccountView(LoginRequiredMixin, View):
    template_name = 'account.html'

    def get(self, request, *args, **kwargs):
        user_profile_form = UserProfileForm(instance=request.user)
        user_documents_formset = UserDocumentsFormSet(queryset=UserDocument.objects.filter(user=request.user))
        return render(request, self.template_name, {
            'user_profile_form': user_profile_form,
            'user_documents_formset': user_documents_formset,
        })

    def post(self, request, *args, **kwargs):
        user_profile_form = UserProfileForm(request.POST, instance=request.user)
        user_documents_formset = UserDocumentsFormSet(request.POST, request.FILES)

        if user_profile_form.is_valid() and user_documents_formset.is_valid():
            user_profile_form.save()
            user_documents_formset.save()
            return redirect(reverse('account'))

        return render(request, self.template_name, {
            'user_profile_form': user_profile_form,
            'user_documents_formset': user_documents_formset,
        })
