from django.core.management.base import BaseCommand, CommandError
from quiz.models import QuizUser
import os, dateparser

class Command(BaseCommand):
    help = 'Generate report for User'

    def add_arguments(self, parser):
        parser.add_argument('start', type=str)
        parser.add_argument('end', type=str)

        parser.add_argument('-u', '--user', nargs='+', type=str)
        parser.add_argument('-a', '--all', action='store_true')
        parser.add_argument('-d', '--debug', action='store_true')

    def handle(self, *args, **options):
        start_str = options['start']
        end_str = options['end']

        usernames = options['user']
        all = options['all']
        debug = options['debug']

        start = dateparser.parse(start_str)
        end = dateparser.parse(end_str)

        users = []

        if all:
            users = QuizUser.objects.all()
        else:
            for username in usernames:
                try:
                    users.append(QuizUser.objects.get(username=username))
                except BaseException:
                    raise CommandError('Error: user not found for username ' + username)