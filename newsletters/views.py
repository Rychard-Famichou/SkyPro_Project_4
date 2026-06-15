from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, DetailView, CreateView, FormView

from .forms import NewsletterForm, RecipientCreateForm, \
    RecipientUpdateForm, MessageForm
from .models import Newsletter, Recipient, Message, UserRecipientLink, Attempt
from .services import send_newsletter


# Create your views here.
@method_decorator(login_not_required, name='dispatch')
class HomePageView(TemplateView):
    template_name = "newsletters/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = cache.get('home_stats')
        if stats is None:
            now = timezone.now()
            stats = {
                'total_newsletters': Newsletter.objects.count(),
                'total_recipients': Recipient.objects.count(),
                'active_newsletters': Newsletter.objects.filter(
                    status=Newsletter.StatusChoices.LAUNCHED,
                    start_time__lte=now,
                    end_time__gte=now,
                ).count(),
            }
            cache.set('home_stats', stats, 60)

        context.update(stats)
        return context


class OwnerMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().owner == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для этого действия")
        return redirect('home')


class OwnerOrStaffMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        return user.is_staff or obj.owner == user

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для этого действия")
        return redirect('home')


class StaffMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для этого действия")
        return redirect('home')


class NewsletterMixin:
    model = Newsletter
    context_object_name = "newsletter"


class NewsletterMixinForm(NewsletterMixin, SuccessMessageMixin):
    form_class = NewsletterForm
    template_name = "newsletters/newsletter_form.html"


class NewsletterCreateView(NewsletterMixinForm, CreateView):
    success_message = "Рассылка создана"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = False
        return context


class NewsletterUpdateView(OwnerMixin, NewsletterMixinForm, UpdateView):
    success_message = "Рассылка обновлена"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context


class NewsletterDetailView(OwnerOrStaffMixin, NewsletterMixin, DetailView):
    template_name = "newsletters/newsletter_detail.html"

    def get_object(self, queryset=None):
        newsletter = super().get_object(queryset)
        newsletter.update_status()  # ← пересчёт и сохранение статуса
        return newsletter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        newsletter = self.object

        cache_key = f"newsletter_stats_{newsletter.pk}"
        cached_data = cache.get(cache_key)

        if cached_data is None:
            attempts = Attempt.objects.filter(mailing=newsletter)

            cached_data = {
                'attempts': list(attempts),
                'total_attempts': attempts.count(),
                'success_attempts': attempts.filter(status=Attempt.StatusChoices.SUCCESS).count(),
                'failure_attempts': attempts.filter(status=Attempt.StatusChoices.FAILURE).count()
            }
            cache.set(cache_key, cached_data, 60 * 15)

        context.update(cached_data)
        return context


class NewsletterListView(NewsletterMixin, ListView):
    template_name = "newsletters/newsletter_list.html"
    context_object_name = "newsletters"

    def get_queryset(self):
        user = self.request.user
        queryset = Newsletter.objects.all()
        if user.is_staff:
            return queryset
        queryset = queryset.filter(owner=user)
        return queryset


class NewsletterDeleteView(OwnerMixin, NewsletterMixin, SuccessMessageMixin, DeleteView):
    template_name = "newsletters/newsletter_delete.html"
    success_url = reverse_lazy('newsletters:newsletter_list')
    success_message = "Рассылка удалена"


class NewsletterSendView(View):
    def post(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)
        if not (
                request.user.is_staff or
                newsletter.owner == request.user
        ):
            messages.error(request, "У вас нет прав")
            return redirect('home')

        if send_newsletter(newsletter, reason="Запуск вручную через сайт"):
            cache.delete(f"newsletter_stats_{newsletter.pk}")
            messages.success(request, "Рассылка успешно выполнена!")
        else:
            messages.error(
                request,
                "Не удалось запустить рассылку. Проверьте её статус и запланированное время."
            )
        return redirect('newsletters:newsletter_detail', pk=newsletter.pk)


class NewsletterBlockView(View):
    def post(self, request, pk):
        if not request.user.is_staff:
            messages.error(request, "У вас нет прав")
            return redirect('home')
        Newsletter.objects.filter(pk=pk).update(status=Newsletter.StatusChoices.BLOCKED)
        messages.success(request, "Рассылка успешно заблокирована.")

        return redirect('newsletters:newsletter_detail', pk=pk)


class NewsletterUnblockView(View):
    def post(self, request, pk):
        if not request.user.is_staff:
            messages.error(request, "У вас нет прав")
            return redirect('home')
        newsletter = get_object_or_404(Newsletter, pk=pk)
        if not newsletter.owner.is_active:
            messages.error(request, "Нельзя разблокировать рассылку, так как её владелец заблокирован.")
            return redirect('newsletters:newsletter_detail', pk=pk)
        newsletter.status = newsletter.StatusChoices.CREATED
        newsletter.save()

        messages.success(request, "Рассылка успешно разблокирована.")
        return redirect('newsletters:newsletter_detail', pk=pk)


class RecipientMixin:
    model = Recipient
    context_object_name = "recipient"


class LinkMixin:
    model = UserRecipientLink
    context_object_name = "link"


class LinkFormMixin(SuccessMessageMixin, LinkMixin):
    template_name = "newsletters/recipient_form.html"


class LinkCreateView(LinkFormMixin, CreateView):
    form_class = RecipientCreateForm
    success_message = "Получатель добавлен в ваш список"

    def form_valid(self, form):
        user = self.request.user

        email_input = form.cleaned_data.get('email')
        recipient, created = Recipient.objects.get_or_create(email=email_input)
        link_exists = UserRecipientLink.objects.filter(
            user=user, recipient=recipient,
        ).exists()
        if link_exists:
            messages.info(self.request, "Этот получатель уже есть в вашем списке")
            return redirect(recipient.get_absolute_url())

        form.instance.user = user
        form.instance.recipient = recipient
        self.object = form.save()

        return redirect(recipient.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = False
        return context


class LinkUpdateView(OwnerMixin, LinkFormMixin, UpdateView):
    form_class = RecipientUpdateForm
    success_message = "Данные получателя обновлены"

    def get_object(self, queryset=None):
        recipient_pk = self.kwargs.get('pk')
        return get_object_or_404(UserRecipientLink, owner=self.request.user, recipient_id=recipient_pk)

    def get_success_url(self):
        return self.object.recipient.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context


class LinkDetailView(OwnerMixin, LinkMixin, DetailView):
    template_name = "newsletters/recipient_detail.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        recipient_pk = kwargs.get('pk')

        if not UserRecipientLink.objects.filter(owner=user, recipient=recipient_pk).exists():
            messages.error(request, "У вас нет прав для этого действия")
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return UserRecipientLink.objects.get(
            owner=self.request.user,
            recipient=self.kwargs.get('pk')
        )


class LinkListView(LinkMixin, ListView):
    """Представление для ПОЛЬЗОВАТЕЛЯ"""
    context_object_name = "links"
    template_name = "newsletters/recipient_list.html"

    def get_queryset(self):
        queryset = UserRecipientLink.objects.filter(owner=self.request.user)
        return queryset


class RecipientDetailView(StaffMixin, RecipientMixin, DetailView):
    template_name = "newsletters/recipient_admin_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_links'] = UserRecipientLink.objects.filter(
            recipient=self.object, ).select_related('owner')
        return context


class RecipientListView(StaffMixin, RecipientMixin, ListView):
    """Представление для МОДЕРАТОРА"""
    context_object_name = "recipients"
    template_name = "newsletters/recipient_admin_list.html"


class LinkDeleteView(OwnerMixin, LinkMixin, DeleteView):
    template_name = "newsletters/recipient_delete.html"
    success_url = reverse_lazy('newsletters:recipient_list')

    def get_object(self, queryset=None):
        return get_object_or_404(
            UserRecipientLink,
            recipient_id=self.kwargs.get('pk'),
            owner=self.request.user,
        )

    def form_valid(self, form):
        link = self.get_object()
        recipient = link.recipient
        link.delete()
        if recipient.userrecipientlink_set.count() == 0:
            recipient.delete()

        messages.success(self.request, "Получатель убран из вашего списка")
        return redirect(self.get_success_url())


class MessageMixin:
    model = Message
    context_object_name = "nl_message"


class MessageMixinForm(MessageMixin, SuccessMessageMixin):
    form_class = MessageForm
    template_name = "newsletters/message_form.html"


class MessageCreateView(MessageMixinForm, CreateView):
    success_message = "Сообщение добавлено в ваш список"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = False
        return context


class MessageUpdateView(OwnerMixin, MessageMixinForm, UpdateView):
    success_message = "Данные сообщения обновлены"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context


class MessageDetailView(OwnerOrStaffMixin, MessageMixin, DetailView):
    template_name = "newsletters/message_detail.html"


class MessageListView(MessageMixin, ListView):
    template_name = "newsletters/message_list.html"
    context_object_name = "nl_messages"

    def get_queryset(self):
        user = self.request.user
        queryset = Message.objects.all()
        if user.is_staff:
            return queryset
        queryset = queryset.filter(owner=user)
        return queryset


class MessageDeleteView(OwnerMixin, MessageMixin, SuccessMessageMixin, DeleteView):
    template_name = "newsletters/message_delete.html"
    success_url = reverse_lazy('newsletters:message_list')
    success_message = "Сообщение удалено из вашего списка"
