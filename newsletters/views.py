from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, DetailView, CreateView

from .forms import NewsletterForm, RecipientForm, MessageForm
from .models import Newsletter, Recipient, Message
from .services import send_newsletter, check_newsletter


# Create your views here.
class HomePageView(TemplateView):
    template_name = "newsletters/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context['total_newsletters'] = Newsletter.objects.count()
        context['total_recipients'] = Recipient.objects.count()

        context['active_newsletters'] = Newsletter.objects.filter(
            status='Запущена',
            start_time__lte=now,
            end_time__gte=now
        ).count()
        
        # all_newsletters = Newsletter.objects.all()
        # active_count = 0
        #
        # for newsletter in all_newsletters:
        #     if check_newsletter(newsletter):
        #         active_count += 1
        #
        # context['active_newsletters'] = active_count

        return context

class NewsletterMixin:
    model = Newsletter
    context_object_name = "newsletter"

class NewsletterMixinForm(NewsletterMixin, SuccessMessageMixin):
    form_class = NewsletterForm
    template_name = "newsletters/newsletter_form.html"

class NewsletterCreateView(NewsletterMixinForm, CreateView):
    success_message = "Рассылка создана"

class NewsletterUpdateView(NewsletterMixinForm, UpdateView):
    success_message = "Рассылка обновлена"

class NewsletterDetailView(NewsletterMixin, DetailView):
    template_name = "newsletters/newsletter_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # ← пересчёт и сохранение статуса
        return obj

class NewsletterListView(NewsletterMixin, ListView):
    template_name = "newsletters/newsletter_list.html"
    context_object_name = "newsletters"

class NewsletterDeleteView(NewsletterMixin, SuccessMessageMixin, DeleteView):
    template_name = "newsletters/newsletter_delete.html"
    success_url = reverse_lazy('newsletters:newsletter_list')
    success_message = "Рассылка удалена"

class NewsletterSendView(View):
    def post(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)
        if send_newsletter(newsletter, reason="Запуск вручную через сайт"):
            messages.success(request, "Рассылка успешно запущена вручную через сайт!")
        else:
            messages.error(
                request,
                "Не удалось запустить рассылку. Проверьте её статус и запланированное время."
            )
        return redirect('newsletters:newsletter_detail', pk=newsletter.pk)

class RecipientMixin:
    model = Recipient
    context_object_name = "recipient"

class RecipientMixinForm(RecipientMixin, SuccessMessageMixin):
    form_class = RecipientForm
    template_name = "newsletters/recipient_form.html"

class RecipientCreateView(RecipientMixinForm, CreateView):
    success_message = "Получатель добавлен в список"

class RecipientUpdateView(RecipientMixinForm, UpdateView):
    success_message = "Получатель в списке обновлён"

class RecipientDetailView(RecipientMixin, DetailView):
    template_name = "newsletters/recipient_detail.html"

class RecipientListView(RecipientMixin, ListView):
    template_name = "newsletters/recipient_list.html"
    context_object_name = "recipients"

class RecipientDeleteView(RecipientMixin, SuccessMessageMixin, DeleteView):
    template_name = "newsletters/recipient_delete.html"
    success_url = reverse_lazy('newsletters:recipient_list')
    success_message = "Получатель убран из списка"

class MessageMixin:
    model = Message
    context_object_name = "nl_message"

class MessageMixinForm(MessageMixin, SuccessMessageMixin):
    form_class = MessageForm
    template_name = "newsletters/message_form.html"

class MessageCreateView(MessageMixinForm, CreateView):
    success_message = "Сообщение добавлено в систему"

class MessageUpdateView(MessageMixinForm, UpdateView):
    success_message = "Сообщение в системе обновлено"

class MessageDetailView(MessageMixin, DetailView):
    template_name = "newsletters/message_detail.html"

class MessageListView(MessageMixin, ListView):
    template_name = "newsletters/message_list.html"
    context_object_name = "nl_messages"

class MessageDeleteView(MessageMixin, SuccessMessageMixin, DeleteView):
    template_name = "newsletters/message_delete.html"
    success_url = reverse_lazy('newsletters:message_list')
    success_message = "Сообщение удалено из системы"
