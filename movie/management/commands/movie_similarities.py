from django.core.management.base import BaseCommand

from movie.ai_utils import EMBEDDING_MODEL, cosine_similarity, get_embedding
from movie.models import Movie


class Command(BaseCommand):
    help = "Compara dos películas y un prompt usando embeddings locales (sentence-transformers)"

    def add_arguments(self, parser):
        parser.add_argument("--movie1", default="Interstellar")
        parser.add_argument("--movie2", default="The Godfather")
        parser.add_argument("--prompt", default="película de ciencia ficción")

    def handle(self, *args, **options):
        # Cambia estos títulos (o usa --movie1/--movie2) para comparar otras películas
        movie1 = Movie.objects.get(title=options["movie1"])
        movie2 = Movie.objects.get(title=options["movie2"])
        prompt = options["prompt"]

        self.stdout.write(f"Modelo de embeddings: {EMBEDDING_MODEL} (local)")
        self.stdout.write(f"Película 1: {movie1.title} ({movie1.genre})")
        self.stdout.write(f"Película 2: {movie2.title} ({movie2.genre})")
        self.stdout.write(f"Prompt: \"{prompt}\"\n")

        # Embeddings de las sinopsis de ambas películas
        emb1 = get_embedding(movie1.synopsis)
        emb2 = get_embedding(movie2.synopsis)

        # Similitud entre películas
        similarity = cosine_similarity(emb1, emb2)
        self.stdout.write(f"\U0001F3AC Similaridad entre '{movie1.title}' y '{movie2.title}': {similarity:.4f}")

        # Similitud del prompt contra cada película
        prompt_emb = get_embedding(prompt)
        sim_prompt_movie1 = cosine_similarity(prompt_emb, emb1)
        sim_prompt_movie2 = cosine_similarity(prompt_emb, emb2)

        self.stdout.write(f"\U0001F4DD Similitud prompt vs '{movie1.title}': {sim_prompt_movie1:.4f}")
        self.stdout.write(f"\U0001F4DD Similitud prompt vs '{movie2.title}': {sim_prompt_movie2:.4f}")
