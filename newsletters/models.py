from django.db import models
from django.urls import reverse
from django.utils import timezone


# Create your models here.
class Recipient(models.Model):
    email = models.CharField(max_length=50, unique=True, verbose_name="Почта")
    full_name = models.CharField(max_length=100, verbose_name="Ф.И.О.")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий")

    def __str__(self):
        return f"Получатель №{self.pk} — {self.email}"

    def get_absolute_url(self):
        # Автоматически отправляет на страницу деталей созданного/измененного товара
        return reverse('newsletters:recipient_detail', kwargs={'pk': self.pk})

class Message(models.Model):
    subject = models.CharField(max_length=50, verbose_name="Тема")
    message = models.TextField(verbose_name="Сообщение")

    def __str__(self):
        return f"Сообщение №{self.pk} — {self.subject}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def get_absolute_url(self):
        # Автоматически отправляет на страницу деталей созданного/измененного товара
        return reverse('newsletters:message_detail', kwargs={'pk': self.pk})


class Newsletter(models.Model):
    class StatusChoices(models.TextChoices):
        CREATED = 'Создана', 'Создана'
        LAUNCHED = 'Запущена', 'Запущена'
        COMPLETED = 'Завершена', 'Завершена'

    start_time = models.DateTimeField(verbose_name="Начало рассылки")
    end_time = models.DateTimeField(verbose_name="Конец рассылки")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.CREATED,
        verbose_name="Статус рассылки"
    )
    message = models.ForeignKey(Message, on_delete=models.PROTECT, verbose_name="Сообщение рассылки")
    recipients = models.ManyToManyField(Recipient, verbose_name="Список получателей")

    def __str__(self):
        return f"Рассылка №{self.pk} — {self.message}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def get_absolute_url(self):
        # Автоматически отправляет на страницу деталей созданного/измененного товара
        return reverse('newsletters:newsletter_detail', kwargs={'pk': self.pk})

    def update_status(self):
        now = timezone.now()

        if now < self.start_time:
            new_status = self.StatusChoices.CREATED
        elif now <= self.end_time:
            new_status = self.StatusChoices.LAUNCHED
        else:
            new_status = self.StatusChoices.COMPLETED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])


class Attempt(models.Model):
    class StatusChoices(models.TextChoices):
        SUCCESS = 'Успешно', 'Успешно'
        FAILURE = 'Не успешно', 'Не успешно'

    attempt_time = models.DateTimeField(verbose_name="Время попытки")
    status = models.CharField(max_length=20,
                              choices=StatusChoices.choices,
                              default=StatusChoices.FAILURE,
                              verbose_name="Статус попытки")
    server_response = models.TextField(verbose_name="Ответ сервера")
    mailing = models.ForeignKey(Newsletter, on_delete=models.CASCADE, verbose_name="Рассылка")

    def __str__(self):
        return f"Попытка {self.pk} для {self.mailing.pk}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
