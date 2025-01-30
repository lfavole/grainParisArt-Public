from datetime import date, datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand

from cinemas.models import Showtime


class Command(BaseCommand):
    def handle(self, **_options):
        today = date.today()

        # Remove old showtimes
        print("Removing old showtimes")
        Showtime.objects.filter(
            start_time__lt=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).delete()

        # Fetch showtimes
        showtimes_count = 0

        for i in range(0, 7):
            day = today + timedelta(i)
            print(f"Fetching showtimes for {day}... ", end="")
            day_showtimes: list[Showtime] = []
            for theater in settings.THEATERS:
                day_showtimes.extend(theater.get_showtimes(day))

            showtimes_count += len(day_showtimes)
            print(f"{len(day_showtimes)} showtimes fetched")

            # Save showtimes
            print("Saving... ", end="")
            Showtime.objects.bulk_create(day_showtimes, ignore_conflicts=True)
            print("OK")
            print()

        print(f"{showtimes_count} showtimes saved")
