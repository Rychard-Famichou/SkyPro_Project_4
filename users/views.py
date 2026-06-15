from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView

from newsletters.views import StaffMixin
from users.models import CustomUser


# Create your views here.
class UserAdminListView(StaffMixin, ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        return CustomUser.objects.filter(is_superuser=False)


class UserAdminDetailView(StaffMixin, DetailView):
    model = CustomUser
    template_name = 'users/user_detail.html'
    context_object_name = 'viewed_user'


class UserToggleActiveView(StaffMixin, View):
    def post(self, request, pk, *args, **kwargs):
        user_to_toggle = get_object_or_404(CustomUser, pk=pk)

        if request.user == user_to_toggle:
            messages.error(request, 'Вы не можете заблокировать самого себя.')
            return redirect('users:user_detail', pk=pk)

        if user_to_toggle.is_superuser:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Нельзя блокировать суперпользователя.")

        user_to_toggle.is_active = not user_to_toggle.is_active
        user_to_toggle.save()

        if user_to_toggle.is_active:
            messages.success(request, f'Пользователь {user_to_toggle.username} успешно разблокирован.')
        else:
            messages.warning(request, f'Пользователь {user_to_toggle.username} был заблокирован.')

        return redirect('users:user_detail', pk=pk)
