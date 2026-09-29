import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from movie.models import Movie

DEFAULT_CSV = "updated_movie_descriptions.csv"


class Command(BaseCommand):
    help = "Actualiza la sinopsis de cada película desde updated_movie_descriptions.csv (columnas Title, Updated Description)"

    def add_arguments(self, parser):
        parser.add_argument("--csv", default=DEFAULT_CSV, help="Ruta del CSV (relativa a la raíz del proyecto)")

    def handle(self, *args, **options):
        csv_path = Path(options["csv"])
        if not csv_path.is_absolute():
            csv_path = Path(settings.BASE_DIR) / csv_path

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"Archivo no encontrado: {csv_path}"))
            return

        updated, not_found = 0, []
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                title = (row.get("Title") or "").strip()
                description = (row.get("Updated Description") or "").strip()
                if not title or not description:
                    continue

                count = Movie.objects.filter(title=title).update(synopsis=description)
                if count:
                    updated += count
                else:
                    not_found.append(title)

        self.stdout.write(self.style.SUCCESS(f"Películas actualizadas: {updated}"))
        if not_found:
            self.stdout.write(self.style.WARNING(f"No encontradas ({len(not_found)}):"))
            for title in not_found:
                self.stdout.write(f"  - {title}")
