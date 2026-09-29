from django.core.management.base import BaseCommand

from movie.ai_utils import build_description_prompt, get_anthropic_client, get_completion
from movie.models import Movie


class Command(BaseCommand):
    help = "Enriquece la sinopsis de la primera película usando Claude (Anthropic API)"

    def handle(self, *args, **kwargs):
        # Carga ANTHROPIC_API_KEY desde el .env de la raíz y crea el cliente de Anthropic
        client = get_anthropic_client()

        movies = Movie.objects.all().order_by("pk")
        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            self.stdout.write(f"Processing: {movie.title}")
            try:
                self.stdout.write(f"Original synopsis: {movie.synopsis}")

                updated_synopsis = get_completion(client, build_description_prompt(movie))
                self.stdout.write(f"Updated synopsis: {updated_synopsis}")

                movie.synopsis = updated_synopsis
                movie.save(update_fields=["synopsis"])
                self.stdout.write(self.style.SUCCESS(f"Updated: {movie.title}"))
            except Exception as e:
                self.stderr.write(f"Failed for {movie.title}: {e}")

            # Solo se procesa la primera película para no gastar API en el aula.
            # El catálogo completo se genera con aux_files/generate_descriptions_batch.py
            # y se carga con `python manage.py update_movies_from_csv`.
            break
