import numpy as np
from django.core.management.base import BaseCommand

from movie.ai_utils import bytes_to_embedding
from movie.models import Movie


class Command(BaseCommand):
    help = "Muestra el embedding almacenado de una película al azar"

    def add_arguments(self, parser):
        parser.add_argument("--n", type=int, default=10, help="Cantidad de valores a mostrar")

    def handle(self, *args, **options):
        movie = Movie.objects.exclude(emb=None).order_by("?").first()
        if movie is None:
            self.stderr.write("No hay películas con embedding. Ejecuta: python manage.py movie_embeddings")
            return

        emb = bytes_to_embedding(movie.emb)
        n = options["n"]
        self.stdout.write(f"\U0001F3AC Película: {movie.title} ({movie.release_year}, {movie.genre})")
        self.stdout.write(f"Sinopsis: {movie.synopsis[:160]}...")
        self.stdout.write(f"Dimensión del embedding: {emb.shape[0]} | dtype: {emb.dtype} | norma: {np.linalg.norm(emb):.4f}")
        with np.printoptions(precision=5, suppress=True):
            self.stdout.write(f"Primeros {n} valores: {emb[:n]}")
