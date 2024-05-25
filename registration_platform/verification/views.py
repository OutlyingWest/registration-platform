from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse

from .forms import UserProfileForm
from .models import UserDocument
from .services import verify_document
from .tasks import verify_document_task


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


class UserDocumentUploadView(LoginRequiredMixin, View):

    def post(self, request):
        document_id = int(request.POST.get('document_id').split('-')[1])
        file = request.FILES.get('file')

        try:
            self.validate_file_size(file)
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': e.message}, status=400)

        document = UserDocument.update_document_file_by_id(document_id, file)
        transaction.on_commit(
            lambda: verify_document_task.delay(document.id)
        )
        return JsonResponse({'status': 'success'})

    @staticmethod
    def validate_file_size(file, maxsize=10 * 2**200):
        filesize = file.size
        if filesize > maxsize:  # 10MB
            raise ValidationError('Максимальный размер файла не должен превышать 10MB')
        return file

