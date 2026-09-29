"""Genera con Claude la sinopsis enriquecida de las películas y la exporta a CSV.

Se ejecuta fuera de manage.py (equivale al CSV que el profesor entregó con el
dataset genérico, pero con los 148 títulos reales del catálogo):

    python aux_files/generate_descriptions_batch.py --limit 5   # piloto
    python aux_files/generate_descriptions_batch.py             # resto del catálogo

Salida: updated_movie_descriptions.csv (raíz del proyecto), columnas Title,Updated Description.
Es reanudable: los títulos que ya están en el CSV no se vuelven a pedir a la API,
así que el piloto no se paga dos veces. Control de gasto: modelo Haiku, max_tokens=150,
máximo 1 reintento por fallo transitorio; si una película falla se registra y se sigue.
Luego se carga en la BD con: python manage.py update_movies_from_csv
"""
import argparse
import csv
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviereviews.settings")

import django  # noqa: E402

django.setup()

from movie.ai_utils import (  # noqa: E402
    CLAUDE_MODEL,
    MAX_OUTPUT_TOKENS,
    build_description_prompt,
    get_anthropic_client,
    request_completion,
)
from movie.models import Movie  # noqa: E402

OUTPUT_CSV = BASE_DIR / "updated_movie_descriptions.csv"
FIELDNAMES = ["Title", "Updated Description"]
MAX_WORKERS = 4
# USD por millón de tokens (entrada, salida) — Claude Haiku 4.5
PRICE_PER_MTOK = (1.00, 5.00)


def load_existing():
    if not OUTPUT_CSV.exists():
        return {}
    with open(OUTPUT_CSV, newline="", encoding="utf-8") as f:
        return {row["Title"]: row["Updated Description"] for row in csv.DictReader(f)}


def write_csv(rows, movies):
    order = [m.title for m in movies if m.title in rows]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for title in order:
            writer.writerow({"Title": title, "Updated Description": rows[title]})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Procesa solo N películas pendientes (piloto)")
    parser.add_argument("--titles", help="Títulos separados por '|' para un piloto dirigido")
    args = parser.parse_args()

    client = get_anthropic_client()
    movies = list(Movie.objects.all().order_by("pk"))
    rows = load_existing()
    pending = [m for m in movies if m.title not in rows]
    if args.titles:
        wanted = {t.strip() for t in args.titles.split("|")}
        pending = [m for m in pending if m.title in wanted]
    pending = pending[: args.limit]
    print(f"Modelo: {CLAUDE_MODEL} | max_tokens: {MAX_OUTPUT_TOKENS} | "
          f"películas: {len(movies)} | ya en CSV: {len(rows)} | a procesar: {len(pending)}")

    failed, truncated = [], []
    tokens_in = tokens_out = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(request_completion, client, build_description_prompt(m)): m for m in pending}
        for i, future in enumerate(as_completed(futures), 1):
            movie = futures[future]
            try:
                text, response = future.result()
                tokens_in += response.usage.input_tokens
                tokens_out += response.usage.output_tokens
                if response.stop_reason == "max_tokens":
                    truncated.append(movie.title)
                rows[movie.title] = text
                print(f"[{i}/{len(pending)}] OK  {movie.title} ({response.usage.output_tokens} tok, {len(text.split())} palabras)")
            except Exception as e:
                failed.append(movie.title)
                print(f"[{i}/{len(pending)}] ERR {movie.title}: {e}")
            if i % 10 == 0:
                write_csv(rows, movies)

    write_csv(rows, movies)
    cost = tokens_in / 1e6 * PRICE_PER_MTOK[0] + tokens_out / 1e6 * PRICE_PER_MTOK[1]
    print(f"Tokens: entrada={tokens_in} salida={tokens_out} | costo estimado: US${cost:.4f}")
    print(f"CSV: {OUTPUT_CSV} ({len(rows)} filas). Fallidas: {len(failed)} | Truncadas por max_tokens: {len(truncated)}")
    if truncated:
        print("Truncadas:", ", ".join(truncated))
    if failed:
        print("Fallidas (vuelve a ejecutar para reintentar):", ", ".join(failed))


if __name__ == "__main__":
    main()
