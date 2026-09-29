import csv
import re

from django.core.management.base import BaseCommand

from movie.models import Movie

CSV_FILE_PATH = 'movie/management/commands/movies_initial.csv'
DEFAULT_POSTER = 'https://placehold.co/300x450?text={}'


def parse_year(value):
    match = re.search(r'\d{4}', value or '')
    return int(match.group()) if match else 0


def parse_duration(value):
    match = re.search(r'\d+', value or '')
    return int(match.group()) if match else 0


class Command(BaseCommand):
    help = 'Carga hasta 100 películas de movies_initial.csv al modelo Movie.'

    def handle(self, *args, **kwargs):
        created_count = 0
        updated_count = 0

        try:
            with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for count, row in enumerate(reader):
                    if count == 100:
                        break

                    title = row['title'].strip()
                    if not title:
                        continue

                    obj, created = Movie.objects.update_or_create(
                        title=title,
                        defaults={
                            'genre': row.get('genre') or '',
                            'release_year': parse_year(row.get('year')),
                            'synopsis': row.get('plot') or '',
                            'poster': row.get('poster') or DEFAULT_POSTER.format(title.replace(' ', '+')),
                            'director': (row.get('director') or '')[:200],
                            'duration': parse_duration(row.get('runtime')),
                            'content_type': 'movie',
                        },
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f'Import completado. Creadas: {created_count}, Actualizadas: {updated_count}'
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {CSV_FILE_PATH}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error inesperado: {e}'))
