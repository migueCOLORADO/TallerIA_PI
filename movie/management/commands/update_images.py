import requests
from django.core.management.base import BaseCommand

from movie.models import Movie
from movie.poster_utils import (
    build_poster_prompt,
    images_dir,
    load_manifest,
    poster_filename,
    poster_url,
    save_png,
)


class Command(BaseCommand):
    """Genera/descarga el póster Higgsfield de la primera película y actualiza `poster`.

    Higgsfield se usa a través de su servidor MCP (disponible para el agente en
    Claude Code), no como API REST desde Django. Por eso la generación ocurre en
    el paso del agente (ver aux_files/README_higgsfield.md), que deja cada job en
    aux_files/higgsfield_posters.json. Este comando toma el resultado de ese job,
    lo descarga en media/movie/images/ y actualiza la película.
    """

    help = "Descarga el póster generado con Higgsfield para la primera película y actualiza poster"

    def handle(self, *args, **kwargs):
        folder = images_dir()
        folder.mkdir(parents=True, exist_ok=True)
        manifest = load_manifest()

        movies = Movie.objects.all().order_by("pk")
        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            try:
                entry = manifest.get(movie.title)
                if not entry or not entry.get("url"):
                    raise LookupError(
                        "no hay generación Higgsfield para esta película. Prompt sugerido:\n"
                        f"{build_poster_prompt(movie)}"
                    )

                self.stdout.write(f"Higgsfield job {entry['job_id']} ({entry['model']})")
                response = requests.get(entry["url"], timeout=60)
                response.raise_for_status()

                filename = poster_filename(movie.title)
                save_png(response.content, folder / filename)

                movie.poster = poster_url(filename)
                movie.save(update_fields=["poster"])
                self.stdout.write(self.style.SUCCESS(f"Saved and updated image for: {movie.title} -> {movie.poster}"))
            except Exception as e:
                self.stderr.write(f"Failed for {movie.title}: {e}")

            # Solo se procesa la primera película (patrón del taller).
            # El catálogo completo se carga con `python manage.py update_images_from_folder`.
            break

        self.stdout.write(self.style.SUCCESS("Process finished (only first movie updated)."))
