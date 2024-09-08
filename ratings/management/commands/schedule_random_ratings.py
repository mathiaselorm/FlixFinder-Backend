from django.core.management.base import BaseCommand
from ratings.tasks import schedule_random_ratings
from django.utils.timezone import now, timedelta

class Command(BaseCommand):
    help = 'Schedule random ratings for users'

    def add_arguments(self, parser):
        parser.add_argument('--time', type=int, default=60, help='Time in seconds to schedule the task')

    def handle(self, *args, **kwargs):
        time_delay = kwargs['time']
        schedule_time = now() + timedelta(seconds=time_delay)
        schedule_random_ratings.apply_async(eta=schedule_time)
        self.stdout.write(f"Random rating task scheduled to run in {time_delay} seconds.")
