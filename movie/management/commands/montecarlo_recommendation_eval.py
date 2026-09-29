import random
import statistics
import time
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from movie.ai_utils import EMBEDDING_MODEL, get_embedding_model, rank_movies
from movie.models import Movie

# Vocabulario para armar prompts aleatorios, tomado de los géneros y temas del catálogo real
GENRES = [
    "acción", "aventura", "animación", "ciencia ficción", "comedia", "crimen", "drama",
    "fantasía", "romance", "terror", "documental", "misterio", "western", "musical",
]
THEMES = [
    "viajes en el tiempo", "la mafia", "una familia disfuncional", "el espacio exterior",
    "dinosaurios", "un robo millonario", "la amistad", "la guerra", "fantasmas",
    "inteligencia artificial", "el narcotráfico", "la música", "un asesino en serie",
    "la realeza", "superhéroes", "magia", "la prisión", "un viaje a la luna",
    "la vida en la oficina", "la venganza", "el amor imposible", "la supervivencia",
    "la tecnología", "un pueblo misterioso", "la escuela", "animales que hablan",
]
MOODS = ["", "emotiva", "divertida", "oscura", "épica", "clásica", "para ver en familia", "de suspenso"]
TEMPLATES = [
    "película de {genre} sobre {theme}",
    "una serie de {genre} {mood} sobre {theme}",
    "quiero ver algo {mood} de {genre}",
    "{theme}",
    "historia {mood} sobre {theme}",
    "{genre} con {theme} y {theme2}",
]


def random_prompt(rng):
    prompt = rng.choice(TEMPLATES).format(
        genre=rng.choice(GENRES),
        theme=rng.choice(THEMES),
        theme2=rng.choice(THEMES),
        mood=rng.choice(MOODS),
    )
    return " ".join(prompt.split())


def percentile(values, pct):
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round(pct / 100 * (len(ordered) - 1))))
    return ordered[index]


class Command(BaseCommand):
    help = (
        "Simulación Monte Carlo del sistema de recomendación: N prompts aleatorios, "
        "verifica que siempre haya una película válida y similitud en [-1, 1], y mide tiempos. "
        "100% local (sentence-transformers), sin llamadas a APIs externas."
    )

    def add_arguments(self, parser):
        parser.add_argument("--n", type=int, default=200, help="Número de simulaciones")
        parser.add_argument("--seed", type=int, default=42, help="Semilla para reproducibilidad")
        parser.add_argument("--output", default="montecarlo_results.txt")

    def handle(self, *args, **options):
        n, seed = options["n"], options["seed"]
        rng = random.Random(seed)
        queryset = Movie.objects.exclude(emb=None)
        catalog_size = queryset.count()
        valid_ids = set(queryset.values_list("pk", flat=True))

        if catalog_size == 0:
            self.stderr.write("No hay películas con embeddings. Ejecuta: python manage.py movie_embeddings")
            return

        # La carga del modelo ocurre una vez por proceso; se mide aparte para no sesgar las corridas
        t0 = time.perf_counter()
        get_embedding_model()
        load_time = time.perf_counter() - t0

        self.stdout.write(f"Monte Carlo: {n} simulaciones | semilla {seed} | {catalog_size} películas con embedding")

        successes, similarities, times, failures = 0, [], [], []
        recommended = {}
        for i in range(1, n + 1):
            prompt = random_prompt(rng)
            try:
                start = time.perf_counter()
                ranking = rank_movies(prompt, queryset)  # embedding del prompt + búsqueda
                elapsed = time.perf_counter() - start

                movie, similarity = ranking[0] if ranking else (None, None)
                if movie is None:
                    raise ValueError("no se retornó película")
                if movie.pk not in valid_ids:
                    raise ValueError(f"película inválida (pk={movie.pk})")
                if not -1.0 <= similarity <= 1.0:
                    raise ValueError(f"similitud fuera de rango: {similarity}")

                successes += 1
                similarities.append(similarity)
                times.append(elapsed)
                recommended[movie.title] = recommended.get(movie.title, 0) + 1
            except Exception as e:
                failures.append((prompt, str(e)))

            if i % 50 == 0:
                self.stdout.write(f"  {i}/{n} corridas...")

        report = self.build_report(
            n, seed, catalog_size, load_time, successes, similarities, times, failures, recommended, rng
        )
        output = Path(options["output"])
        if not output.is_absolute():
            output = Path(settings.BASE_DIR) / output
        output.write_text(report, encoding="utf-8")

        self.stdout.write(report)
        self.stdout.write(self.style.SUCCESS(f"Resultados guardados en {output}"))

    def build_report(self, n, seed, catalog_size, load_time, successes, similarities, times, failures, recommended, rng):
        ms = [t * 1000 for t in times]
        lines = [
            "=" * 64,
            "SIMULACIÓN MONTE CARLO — SISTEMA DE RECOMENDACIÓN",
            "=" * 64,
            f"Fecha:                    {datetime.now():%Y-%m-%d %H:%M:%S}",
            f"Modelo de embeddings:     {EMBEDDING_MODEL} (local, sin APIs externas)",
            f"Películas con embedding:  {catalog_size}",
            f"Simulaciones (N):         {n}",
            f"Semilla aleatoria:        {seed}",
            f"Carga del modelo:         {load_time:.2f} s (una vez, excluida de los tiempos)",
            "",
            "--- Validez ---",
            f"Éxitos:                   {successes}/{n} ({successes / n * 100:.1f} %)",
            f"Fallos:                   {len(failures)}",
        ]
        if similarities:
            lines += [
                f"Similitud en [-1, 1]:     {'sí' if all(-1 <= s <= 1 for s in similarities) else 'NO'}",
                "",
                "--- Similitud coseno de la película recomendada ---",
                f"Promedio:                 {statistics.mean(similarities):.4f}",
                f"Desviación estándar:      {statistics.pstdev(similarities):.4f}",
                f"Mínima:                   {min(similarities):.4f}",
                f"Máxima:                   {max(similarities):.4f}",
                "",
                "--- Tiempo de respuesta (embedding del prompt + búsqueda) ---",
                f"Promedio:                 {statistics.mean(ms):.1f} ms",
                f"Mediana (p50):            {statistics.median(ms):.1f} ms",
                f"p95:                      {percentile(ms, 95):.1f} ms",
                f"Mínimo:                   {min(ms):.1f} ms",
                f"Máximo:                   {max(ms):.1f} ms",
                f"Total de las corridas:    {sum(times):.2f} s",
                "",
                f"--- Diversidad: {len(recommended)} películas distintas recomendadas ---",
            ]
            for title, count in sorted(recommended.items(), key=lambda kv: -kv[1])[:10]:
                lines.append(f"  {count:3d}x  {title}")
        if failures:
            lines += ["", "--- Fallos ---"] + [f"  {p!r}: {e}" for p, e in failures[:20]]

        lines += ["", "--- Ejemplos de prompts generados ---"]
        example_rng = random.Random(seed)
        lines += [f"  - {random_prompt(example_rng)}" for _ in range(5)]
        lines.append("=" * 64)
        return "\n".join(lines) + "\n"
