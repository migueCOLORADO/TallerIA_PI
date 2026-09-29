import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from news.models import News

CSV_FILE_PATH = 'news/management/commands/Fake.csv'


class Command(BaseCommand):
    help = 'Carga las primeras 5 noticias válidas de Fake.csv al modelo News.'

    def handle(self, *args, **kwargs):
        created_count = 0

        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                if created_count == 5:
                    break

                try:
                    date_value = datetime.strptime(row['date'].strip(), '%B %d, %Y').date()
                except ValueError:
                    continue

                News.objects.update_or_create(
                    headline=row['title'].strip(),
                    defaults={
                        'body': row['text'],
                        'date': date_value,
                    },
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'{created_count} noticias creadas desde Fake.csv.'))
