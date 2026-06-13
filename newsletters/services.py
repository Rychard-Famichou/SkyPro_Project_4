import logging

from django.core.mail import send_mail
from django.utils import timezone

from config import settings
from .models import Attempt


logger = logging.getLogger(__name__)


def check_status(status):
    return status == "Запущена"


def check_time(newsletter):
    now = timezone.now()
    return newsletter.start_time < now <= newsletter.end_time


def check_newsletter(newsletter):
    if check_status(newsletter.status) and check_time(newsletter):
        return True
    return None

def collect_attempts(batch):
    if batch:
        Attempt.objects.bulk_create(batch)


def send_newsletter(newsletter, reason=None):
    """
    Выполняет рассылку для переданного объекта Newsletter.
    Возвращает кортеж: (bool, description_message)
    """
    # 1. Валидация статуса
    if not check_status(newsletter.status):
        return False, f"Рассылка пропущена: текущий статус '{newsletter.status}', а должен быть 'Запущена'."
    # 2. Валидация времени
    if not check_time(newsletter):
        return False, f"Рассылка пропущена: текущее время не входит в интервал [{newsletter.start_time} - {newsletter.end_time}]."
    # 3. Получение списка email-адресов
    recipients_list = list(newsletter.recipients.values_list('email', flat=True))
    if not recipients_list:
        return False, "Рассылка отменена: список получателей пуст."
    # 4. Подготовка данных для отправки
    attempts_to_create = []
    prefix = f"[{reason}] " if reason else ""
    # Кэшируем тему и текст, чтобы Django не делал ленивые запросы к newsletter.message в цикле
    try:
        subject = newsletter.message.subject
        message = newsletter.message.message
    except AttributeError:
        return False, "Ошибка: у рассылки не привязано сообщение (внешний ключ пуст)."
    # 5. Цикл отправки
    for email in recipients_list:
        current_time = timezone.now()
        try:
            # Ограничиваем таймаут соединения (хорошая практика для продакшена)
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )

            status = Attempt.StatusChoices.SUCCESS
            server_response = f"{prefix}Письмо успешно отправлено на адрес {email}."

        except Exception as e:
            status = Attempt.StatusChoices.FAILURE
            server_response = f"{prefix}Ошибка при отправке на {email}: {str(e)}"
            # Логируем ошибку в системный лог (полезно для отладки)
            logger.error(f"Ошибка при отправке на {email}: {str(e)}")

        attempts_to_create.append(
            Attempt(
                attempt_time=current_time,
                status=status,
                server_response=server_response,
                mailing=newsletter
            )
        )
    # 6. Массовое сохранение логов в БД одним запросом
    if attempts_to_create:
        Attempt.objects.bulk_create(attempts_to_create)

    return True, f"Рассылка успешно обработана. Отправлено писем: {len(attempts_to_create)}."
