from django.core.mail import send_mail
from django.utils import timezone

from config import settings
from .models import Attempt


def check_status(status):
    if status == 'Запущена':
        return True
    return None


def check_time(newsletter):
    now = timezone.now()
    if newsletter.start_time < now <= newsletter.end_time:
        return True
    return None


def check_newsletter(newsletter):
    if check_status(newsletter.status) and check_time(newsletter):
        return True
    return None

def collect_attempts(batch):
    if batch:
        Attempt.objects.bulk_create(batch)


def send_newsletter(newsletter, reason=None):
    if check_newsletter(newsletter):
        recipients_list = list(newsletter.recipients.values_list('email', flat=True))
        if not recipients_list:
            print("Список получателей пуст")
            return

        attempts_to_create = []

        for email in recipients_list:
            try:
                message = newsletter.message.message
                subject = newsletter.message.subject
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

                status = Attempt.StatusChoices.SUCCESS
                prefix = f"[{reason}] " if reason else ""
                server_response = f"{prefix}Письмо успешно отправлено на адрес {email}."

            except Exception as e:
                status = Attempt.StatusChoices.FAILURE
                prefix = f"[{reason}] " if reason else ""
                server_response = f"{prefix}Ошибка: {str(e)}"

            attempts_to_create.append(
                Attempt(
                    attempt_time=timezone.now(),
                    status=status,
                    server_response=server_response,
                    mailing=newsletter
                ))
        collect_attempts(attempts_to_create)
        return True
    else:
        print("Попытка отправить рассылку в незапланированное время.")
        return False


# send_newsletter(newsletter, reason="Автоматический запуск из консоли")