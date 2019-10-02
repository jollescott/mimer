from django.core.management.base import BaseCommand, CommandError
from quiz.models import QuizUser, Test, Answer
import os
import dateparser
import dateparser
import datetime
import openpyxl


class Command(BaseCommand):
    help = 'Generate report for User'

    def add_intro(self):
        self.sheet.title = self.user.username

        self.sheet['A1'] = 'Name'
        self.sheet['A2'] = self.user.username

        self.sheet['B1'] = 'Final Score'
        self.sheet['B2'] = self.user.overall_score

        self.sheet['C1'] = 'Completed quizzes'
        self.sheet['C2'] = len(self.tests)

        correct = list(filter(lambda x: x.correct == True, self.answers))

        self.sheet['D1'] = 'Correct ratio'
        self.sheet['D2'] = len(
            correct) / len(self.answers) if len(self.answers) > 0 else 0

        self.sheet['E1'] = 'Sana?'
        self.sheet['E2'] = str(self.user.sana)

        self.cursor = 4

    def plot_tests(self):

        self.sheet['A{0}'.format(self.cursor)] = 'Date'
        self.sheet['B{0}'.format(self.cursor)] = 'Correct percentage'

        test_count = len(self.tests)
        empty_y = self.cursor + 1

        for i in range(0, test_count):
            test = self.tests[i]
            answers = test.answers.all()
            correct = list(filter(lambda x: x.correct == True, answers))

            self.sheet['A{0}'.format(
                i + empty_y)] = test.date.strftime("%d %m %Y %H:%M")
            self.sheet['B{0}'.format(i + empty_y)] = len(correct) / \
                len(answers) if len(answers) > 0 else 0

            self.cursor = self.cursor + 1

        x_values = openpyxl.chart.Reference(
            self.sheet, min_col=1, min_row=empty_y, max_row=empty_y+test_count)

        y_values = openpyxl.chart.Reference(
            self.sheet, min_col=2, min_row=empty_y, max_row=empty_y+test_count)

        chart = openpyxl.chart.LineChart()
        chart.add_data(y_values)
        chart.set_categories(x_values)
        chart.title = 'Test score over time'

        chart.x_axis.number_format = 'dd mm yyyy HH:MM'
        chart.x_axis.title = 'Date'
        chart.y_axis.title = 'Correct percentage'
        self.sheet.add_chart(chart, 'D{0}'.format(empty_y))

        self.cursor = test_count + self.cursor + 2

    def plot_timing(self):
        self.sheet['A{0}'.format(self.cursor)] = 'Date'
        self.sheet['B{0}'.format(self.cursor)] = 'Average Reaction Time'

        test_count = len(self.tests)
        empty_y = self.cursor + 1

        for i in range(0, test_count):
            test = self.tests[i]
            answers = test.answers.all()
            reaction_times = [answer.time for answer in answers]

            reaction_average = sum(
                reaction_times) / len(reaction_times) if len(reaction_times) > 0 else 0

            self.sheet['A{0}'.format(
                i + empty_y)] = test.date.strftime("%d %m %Y %H:%M")
            self.sheet['B{0}'.format(i + empty_y)] = reaction_average

            self.cursor = self.cursor + 1

        x_values = openpyxl.chart.Reference(
            self.sheet, min_col=1, min_row=empty_y, max_row=empty_y+test_count)

        y_values = openpyxl.chart.Reference(
            self.sheet, min_col=2, min_row=empty_y, max_row=empty_y+test_count)

        chart = openpyxl.chart.LineChart()
        chart.add_data(y_values)
        chart.set_categories(x_values)
        chart.title = 'Average reaction rime over time'

        chart.x_axis.number_format = 'dd mm yyyy HH:MM'
        chart.x_axis.title = 'Date'
        chart.y_axis.title = 'Correct percentage'
        self.sheet.add_chart(chart, 'D{0}'.format(empty_y))

        self.cursor = test_count + self.cursor + 2

    def scale_columns(self):
        for col in self.sheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            self.sheet.column_dimensions[column].width = adjusted_width

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

        naive_start = dateparser.parse(start_str)
        naive_end = dateparser.parse(end_str)

        self.start = naive_start.replace(tzinfo=datetime.timezone.utc)
        self.end = naive_end.replace(tzinfo=datetime.timezone.utc)

        users = []

        if all:
            users = QuizUser.objects.all()
        else:
            for username in usernames:
                try:
                    users.append(QuizUser.objects.get(username=username))
                except BaseException:
                    raise CommandError(
                        'Error: user not found for username ' + username)

        if os.path.exists('reports') is not True:
            os.mkdir('reports')

        timestamp = datetime.datetime.now().isoformat()
        os.mkdir('reports/{0}'.format(timestamp))

        for user in users:
            wb = openpyxl.Workbook()
            sheet = wb.active

            self.sheet = sheet
            self.user = user
            self.cursor = 1

            self.tests = Test.objects.filter(user=self.user).filter(
                date__range=[self.start, self.end]).order_by('date')
            self.answers = Answer.objects.filter(user=self.user).filter(
                date__range=[self.start, self.end]).order_by('date')

            self.add_intro()
            self.plot_tests()
            self.plot_timing()

            self.scale_columns()
            wb.save('reports/{0}/{1}.xlsx'.format(timestamp, user.username))
