from django.core.management.base import BaseCommand

from movie.models import Movie
from movie.poster_utils import images_dir, poster_filename, poster_url


class Command(BaseCommand):
    help = "Asigna a cada película el póster m_<title_slug>.png que exista en media/movie/images/"

    def handle(self, *args, **kwargs):
        folder = images_dir()
        if not folder.exists():
            self.stderr.write(self.style.ERROR(f"No existe la carpeta {folder}"))
            return

        files = {p.name for p in folder.glob("m_*.png")}
        by_filename = {poster_filename(m.title): m for m in Movie.objects.all()}

        updated, unmatched = 0, []
        for filename in sorted(files):
            movie = by_filename.get(filename)
            if movie is None:
                unmatched.append(filename)
                continue
            movie.poster = poster_url(filename)
            movie.save(update_fields=["poster"])
            updated += 1

        missing = sorted(m.title for f, m in by_filename.items() if f not in files)

        self.stdout.write(self.style.SUCCESS(f"Pósters asignados: {updated} (archivos en carpeta: {len(files)})"))
        if unmatched:
            self.stdout.write(self.style.WARNING(f"Archivos sin película asociada ({len(unmatched)}): {', '.join(unmatched)}"))
        if missing:
            self.stdout.write(self.style.WARNING(f"Películas sin archivo de póster ({len(missing)}): {', '.join(missing)}"))
