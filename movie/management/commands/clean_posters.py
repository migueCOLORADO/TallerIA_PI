from django.core.management.base import BaseCommand

from movie.management.commands.add_movies_db import DEFAULT_POSTER, clean_poster
from movie.models import Movie


class Command(BaseCommand):
    help = "Repara posters invalidos ya guardados en BD (N/A, vacios, URLs malformadas) con el placeholder."

    def handle(self, *args, **kwargs):
        fixed = 0
        for movie in Movie.objects.all():
            # Las rutas locales de media (/media/...) son válidas aunque no empiecen por http
            if (movie.poster or '').startswith('/media/'):
                continue
            if not clean_poster(movie.poster):
                movie.poster = DEFAULT_POSTER.format(movie.title.replace(' ', '+'))
                movie.save(update_fields=["poster"])
                fixed += 1
        self.stdout.write(self.style.SUCCESS(f"Posters reparados: {fixed}"))
