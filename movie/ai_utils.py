"""Utilidades de IA compartidas por comandos, vistas y tests (Taller 3).

- Claude (Anthropic API) para enriquecer sinopsis.
- sentence-transformers (modelo local) para embeddings y similitud coseno.
"""
import os
from functools import lru_cache
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

# Haiku: el modelo más económico de Claude; suficiente para enriquecer una sinopsis corta.
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5")
MAX_OUTPUT_TOKENS = 150
# Variante multilingüe de MiniLM (384 dims): las sinopsis y los prompts están en español,
# y all-MiniLM-L6-v2 está entrenado casi solo en inglés.
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
EMB_DTYPE = np.float32


# ---------------------------------------------------------------------------
# Claude
# ---------------------------------------------------------------------------

def get_anthropic_client():
    """Crea el cliente de Anthropic leyendo ANTHROPIC_API_KEY desde el .env de la raíz."""
    import anthropic
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY no está definida. Agrégala al archivo .env en la raíz del proyecto."
        )
    # max_retries=1: como máximo un reintento automático por fallo transitorio (429/5xx/red)
    return anthropic.Anthropic(api_key=api_key, max_retries=1)


def build_description_prompt(movie):
    return (
        "Eres un crítico de cine que escribe fichas para un catálogo en español.\n"
        f"Película: {movie.title} ({movie.release_year}).\n"
        f"Género: {movie.genre}. Director: {movie.director}.\n"
        f"Sinopsis actual: {movie.synopsis}\n\n"
        "Reescribe y enriquece la sinopsis en español neutro, en un solo párrafo de "
        "50 a 80 palabras: presenta la premisa, el conflicto principal, el tono y los "
        "temas de la película, sin revelar el final. Responde únicamente con la sinopsis, "
        "sin título, sin comillas y sin comentarios adicionales."
    )


def request_completion(client, prompt, model=CLAUDE_MODEL):
    """Envía un prompt a Claude y retorna (texto, response) para poder leer usage/stop_reason."""
    response = client.messages.create(
        model=model,
        max_tokens=MAX_OUTPUT_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude rechazó la solicitud: {response.stop_details}")
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    if not text:
        raise RuntimeError(f"Respuesta vacía (stop_reason={response.stop_reason})")
    return text, response


def get_completion(client, prompt, model=CLAUDE_MODEL):
    """Envía un prompt a Claude y retorna el texto de la respuesta."""
    return request_completion(client, prompt, model)[0]


# ---------------------------------------------------------------------------
# Embeddings locales (sentence-transformers)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_embedding_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL)


def get_embedding(text):
    """Embedding normalizado (float32) de un texto con el modelo local."""
    vector = get_embedding_model().encode(text, normalize_embeddings=True)
    return np.asarray(vector, dtype=EMB_DTYPE)


def get_embeddings(texts, batch_size=32):
    vectors = get_embedding_model().encode(
        list(texts), batch_size=batch_size, normalize_embeddings=True
    )
    return np.asarray(vectors, dtype=EMB_DTYPE)


def embedding_to_bytes(vector):
    return np.asarray(vector, dtype=EMB_DTYPE).tobytes()


def bytes_to_embedding(data):
    return np.frombuffer(bytes(data), dtype=EMB_DTYPE)


def cosine_similarity(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.clip(np.dot(a, b) / denom, -1.0, 1.0))


def recommend_movie(prompt, queryset=None):
    """Retorna (película, similitud) con mayor similitud coseno al prompt, o (None, None)."""
    from .models import Movie

    if queryset is None:
        queryset = Movie.objects.exclude(emb=None)

    prompt_emb = get_embedding(prompt)
    best_movie, best_similarity = None, -np.inf
    for movie in queryset:
        similarity = cosine_similarity(prompt_emb, bytes_to_embedding(movie.emb))
        if similarity > best_similarity:
            best_movie, best_similarity = movie, similarity

    if best_movie is None:
        return None, None
    return best_movie, best_similarity
