from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        # Если регистрируется суперпользователь или адрес содержит нужный email,
        # то просто автоматически подтверждаем email без отправки письма
        user = emailconfirmation.email_address.user
        if user.is_superuser or user.email == "admin@example.com":
            emailconfirmation.email_address.verified = True
            emailconfirmation.email_address.save()
            return  # Письмо не отправляется

        # Для всех остальных пользователей стандартная отправка
        super().send_confirmation_mail(request, emailconfirmation, signup)

    def respond_email_verification_sent(self, request, user):
        # Если это админ, перенаправляем на главную (или в админку) БЕЗ всплывающего сообщения
        if user.is_superuser or user.email == "admin@example.com":
            return redirect(settings.LOGIN_REDIRECT_URL)

        # Для обычных пользователей показываем стандартную страницу "Письмо отправлено"
        return super().respond_email_verification_sent(request, user)
