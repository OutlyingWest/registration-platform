import asyncio

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse

from .forms import UserDocumentsFormSet, UserProfileForm, UserDocumentForm
from .models import UserDocument
from .services import verify_document


class UserAccountView(LoginRequiredMixin, View):
    template_name = 'account.html'

    def get(self, request, *args, **kwargs):
        user_profile_form = UserProfileForm(instance=request.user)
        user_documents = UserDocument.objects.filter(user=request.user)
        return render(request, self.template_name, {
            'user_profile_form': user_profile_form,
            'user_documents': user_documents,
        })

    def post(self, request, *args, **kwargs):
        user_profile_form = UserProfileForm(request.POST, instance=request.user)

        if user_profile_form.is_valid():
            user_profile_form.save()
            return redirect(reverse('account'))

        user_documents = UserDocument.objects.filter(user=request.user)
        return render(request, self.template_name, {
            'user_profile_form': user_profile_form,
            'user_documents': user_documents,
        })


class UserDocumentUploadView(View):
    async def post(self, request):
        print(f'{request.POST=}')
        print(f'{request.FILES=}')
        document_id = int(request.POST.get('document_id').split('-')[1])
        file = request.FILES.get('file')

        document = await UserDocument.update_document_file_by_id(document_id, file)
        print(f'{document=}')
        asyncio.create_task(verify_document(document))
        return JsonResponse({'document_id': document.id, 'new_status': 'uploaded'})
