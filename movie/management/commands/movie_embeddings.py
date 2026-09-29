from django.core.management.base import BaseCommand

from movie.ai_utils import EMBEDDING_MODEL, embedding_to_bytes, get_embeddings, movie_document
from movie.models import Movie


class Command(BaseCommand):
    help = "Genera y guarda (campo emb) el embedding de todas las películas (título, género y sinopsis)"

    def handle(self, *args, **kwargs):
        movies = list(Movie.objects.all().order_by("pk"))
        self.stdout.write(f"Found {len(movies)} movies in the database")
        self.stdout.write(f"Modelo de embeddings: {EMBEDDING_MODEL} (local)")

        embeddings = get_embeddings(movie_document(m) for m in movies)

        for movie, emb in zip(movies, embeddings):
            try:
                # Se guarda el vector float32 como binario en la base de datos
                movie.emb = embedding_to_bytes(emb)
                movie.save(update_fields=["emb"])
                self.stdout.write(self.style.SUCCESS(f"✅ Embedding stored for: {movie.title}"))
            except Exception as e:
                self.stderr.write(f"❌ Failed to store embedding for {movie.title}: {e}")

        self.stdout.write(self.style.SUCCESS(
            f"\U0001F3AF Finished generating embeddings for {len(movies)} movies "
            f"(dimensión {embeddings.shape[1] if len(movies) else 0})"
        ))
