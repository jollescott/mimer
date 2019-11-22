from django.core.management.base import BaseCommand, CommandError
from quiz.models import QuizUser, Test, Answer, Asset
from datetime import datetime, timezone
import os
import dateparser
import dateparser
import openpyxl
import statistics
import random
import string

class Result():
    def __init__(self, username, sana):
        self.username = username

        self.score = 0
        self.completed_quizzes = 0
        self.content_coverage = 0

        self.test_results = []
        self.reaction_times = []

        self.sana = sana


class Command(BaseCommand):
    help = 'Generate report for User'

    def random_string(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def add_intro(self):
        self.sheet.title = self.current_result.username

        self.sheet['A1'] = 'Name'
        self.sheet['A2'] = self.current_result.username

        self.sheet['B1'] = 'Final Score'
        self.sheet['B2'] = self.current_result.score

        self.sheet['C1'] = 'Completed quizzes'
        self.sheet['C2'] = self.current_result.completed_quizzes

        self.sheet['D1'] = 'Content coverage'
        self.sheet['D2'] = self.current_result.content_coverage

        self.sheet['E1'] = 'Sana?'
        self.sheet['E2'] = str(self.current_result.sana)

        self.cursor = 4

    def plot_tests(self):

        self.sheet['A{0}'.format(self.cursor)] = 'Date'
        self.sheet['B{0}'.format(self.cursor)] = 'Correct percentage'

        test_count = len(self.current_result.test_results)
        empty_y = self.cursor + 1

        for i in range(0, test_count):
            test = self.current_result.test_results[i]

            self.sheet['A{0}'.format(
                i + empty_y)] = test['date'].strftime("%d %m %Y %H:%M")
            self.sheet['B{0}'.format(i + empty_y)] = test['score']

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
        self.sheet['B{0}'.format(self.cursor)] = 'Average Reaction Time (ms)'

        test_count = len(self.current_result.reaction_times)
        empty_y = self.cursor + 1

        for i in range(0, test_count):
            reaction_time = self.current_result.reaction_times[i]
            self.sheet['A{0}'.format(
                i + empty_y)] = reaction_time['date'].strftime("%d %m %Y %H:%M")
            self.sheet['B{0}'.format(i + empty_y)] = reaction_time['score']

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
        chart.y_axis.title = 'Time (ms)'
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

    def produce_report(self):
        wb = openpyxl.Workbook()
        sheet = wb.active

        self.sheet = sheet
        self.cursor = 1

        self.add_intro()
        self.plot_tests()
        self.plot_timing()

        self.scale_columns()
        wb.save('reports/{0}/{1}.xlsx'.format(self.timestamp,
                                              self.current_result.username))

    def create_average_result(self, username, sana, user_group):
        result = Result(username, sana)

        result.score = statistics.mean(
            [user.score for user in user_group])

        result.content_coverage = statistics.mean(
            [user.content_coverage for user in user_group])

        result.completed_quizzes = statistics.mean(
            [user.completed_quizzes for user in user_group])

        result.test_results = []

        dates = []

        for user in user_group:
            for test in user.test_results:
                dates.append(test['date'].date())

        dates = set(dates)
        dates = sorted(dates)

        for date in dates:
            date_tests = []

            for user in user_group:
                for test in user.test_results:
                    if test['date'].date() == date:
                        date_tests.append(test)

            test_scores = [test['score'] for test in date_tests]
            median = statistics.mean(test_scores)

            result.test_results.append({
                'date': datetime.combine(date, datetime.min.time()),
                'score': median
            })

            date_reactions = []

            for user in user_group:
                for reaction_time in user.reaction_times:
                    if reaction_time['date'].date() == date:
                        date_reactions.append(reaction_time)

            reaction_times = [reaction['score'] for reaction in date_reactions]
            median = statistics.mean(reaction_times)

            result.reaction_times.append({
                'date': datetime.combine(date, datetime.min.time()),
                'score': median
            })

        return result

    def add_arguments(self, parser):
        parser.add_argument('start', type=str)
        parser.add_argument('end', type=str)

        parser.add_argument('-u', '--user', nargs='+', type=str)
        parser.add_argument('-e', '--exclude', nargs='+', type=str)
        parser.add_argument('-a', '--all', action='store_true')
        parser.add_argument('-d', '--debug', action='store_true')
        parser.add_argument('-an', '--anon', action='store_true')

    def handle(self, *args, **options):
        # Load options
        start_str = options['start']
        end_str = options['end']

        usernames = options['user']
        excluded = options['exclude']
        all_users = options['all']
        anon = options['anon']

        # Timing
        naive_start = dateparser.parse(
            start_str, settings={'DATE_ORDER': 'DMY'})
        naive_end = dateparser.parse(end_str, settings={'DATE_ORDER': 'DMY'})

        self.start = naive_start.replace(tzinfo=timezone.utc)
        self.end = naive_end.replace(tzinfo=timezone.utc)

        # Assets
        self.asset_ids = Asset.objects.values_list('id', flat=True)

        # Load usernames
        users = []

        if all_users:
            users = QuizUser.objects.all()
        else:
            if usernames is None:
                raise CommandError(
                    'Error: no users were passed')

            for username in usernames:
                try:
                    users.append(QuizUser.objects.get(username=username))
                except BaseException:
                    raise CommandError(
                        'Error: user not found for username ' + username)

        if excluded:
            users = [user for user in users if user.username not in excluded]

        # Create report folder
        if os.path.exists('reports') is not True:
            os.mkdir('reports')

        self.timestamp = int(datetime.now().timestamp())
        os.mkdir('reports/{0}'.format(self.timestamp))

        # Load user results
        results = []

        for user in users:
            result = Result(self.random_string() if anon else user.username, user.sana)

            # Load all completed tests in date range
            tests = Test.objects.filter(user=user, complete=True).filter(
                date__range=[self.start, self.end]).order_by('date')

            # Load all answers
            answers = Answer.objects.filter(user=user).filter(
                date__range=[self.start, self.end]).order_by('date')

            result.score = user.overall_score
            result.completed_quizzes = len(tests)

            # Which percentage of the assets has the user trained on?
            covered_ids = [answer.question.asset.id for answer in answers]
            covered_ids = set(covered_ids)

            result.content_coverage = len(
                covered_ids) / len(self.asset_ids) if len(self.asset_ids) > 0 else 0

            # Score and reaction time results
            result.test_results = []
            result.reaction_times = []

            for test in tests:
                test_answers = test.answers.all()

                # Correct ratio
                correct = list(
                    filter(lambda x: x.correct == True, test_answers))
                score = len(correct) / \
                    len(test_answers) if len(test_answers) > 0 else 0

                result.test_results.append({
                    "date": test.date,
                    "score": score
                })

                # Median of reaction times
                reaction_times = [answer.time for answer in test_answers]
                reaction_average = statistics.median(reaction_times)

                result.reaction_times.append({
                    "date": test.date,
                    "score": reaction_average
                })

            results.append(result)
            print('[DONE] result generated for {}'.format(user.username))

        normal_users = [
            result for result in results if result.sana is not True]
        sana_users = [result for result in results if result.sana]

        if normal_users:
            result = self.create_average_result(
                'normal_average', False, normal_users)
            results.append(result)

        if sana_users:
            result = self.create_average_result(
                'sana_average', True, sana_users)
            results.append(result)

        for result in results:
            self.current_result = result
            self.produce_report()
            print('[DONE] Report produced for {}'.format(result.username))
