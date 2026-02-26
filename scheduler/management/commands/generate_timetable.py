# scheduler/management/commands/generate_timetable.py
from django.core.management.base import BaseCommand
from scheduler.generator import generate_timetable

class Command(BaseCommand):
    help = "Generate a timetable using the scheduler.generator logic"

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=5)
        parser.add_argument('--periods', type=int, default=6)

    def handle(self, *args, **options):
        self.stdout.write("Generating timetable...")

        success, message = generate_timetable(
            days=options['days'],
            periods_per_day=options['periods']
        )

        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.ERROR(message))
