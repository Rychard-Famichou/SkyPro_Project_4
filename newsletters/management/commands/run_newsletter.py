from django.core.management.base import BaseCommand, CommandError
from newsletters.models import Newsletter
from newsletters.services import send_newsletter


class Command(BaseCommand):
    help = 'Runs the newsletter via CLI'

    def add_arguments(self, parser):
        parser.add_argument('newsletter_id', type=int, help='ID of the newsletter to send')

    def handle(self, *args, **options):
        newsletter_id = options['newsletter_id']

        try:
            newsletter = Newsletter.objects.select_related('message').get(pk=newsletter_id)
        except Newsletter.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Рассылка с ID {newsletter_id} не существует.'))
            return

        self.stdout.write(f'Выполняю рассылку с ID {newsletter_id}...')

        success, message = send_newsletter(newsletter, reason='CLI')

        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.WARNING(message))
