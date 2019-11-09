from django.core.management.base import BaseCommand, CommandError
from quiz.models import QuizUser
from webpush import send_user_notification


class Command(BaseCommand):
    help = 'Syncs Database with Sana Assets.'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--debug', action='store_true')

    def handle(self, *args, **options):
        users = QuizUser.objects.all()
        payload = {'head': 'Ditt dagliga test på Grönländska glosor!',
                   'body': 'Klicka för att påbörja ett nytt test. Tack igen för att du deltar i vårt gymnasiearbete :)'}

        for user in users:
            try:
                send_user_notification(user, payload, 1000)
            except BaseException as ex:
                print(ex)