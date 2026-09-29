"""Utilidades para los pósters generados con Higgsfield (Taller 3)."""
import io
import json
from pathlib import Path

from django.conf import settings
from django.utils.text import slugify

IMAGES_SUBDIR = "movie/images"
MANIFEST_PATH = Path(settings.BASE_DIR) / "aux_files" / "higgsfield_posters.json"
POSTER_SIZE = (360, 480)  # 3:4, suficiente para las cards del catálogo


def poster_filename(title):
    return f"m_{slugify(title)}.png"


def images_dir():
    return Path(settings.MEDIA_ROOT) / IMAGES_SUBDIR


def poster_url(filename):
    return f"{settings.MEDIA_URL}{IMAGES_SUBDIR}/{filename}"


def build_poster_prompt(movie):
    # El título NO va en el prompt: si aparece, el modelo tiende a escribirlo (mal) en la imagen.
    kind = "TV series" if movie.content_type == "series" else "film"
    return (
        f"Textless cinematic key art illustration for a {movie.genre} {kind} from {movie.release_year}. "
        f"Scene: {movie.synopsis[:400]} "
        "Painterly digital illustration, dramatic lighting, rich colors, strong central composition. "
        "Original characters, no real actors' likeness. Pure artwork only: no typography, "
        "no lettering, no captions, no logos, no watermark."
    )


def load_manifest():
    if not MANIFEST_PATH.exists():
        return {}
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return {item["title"]: item for item in json.load(f)}


def save_png(image_bytes, destination):
    """Normaliza la imagen descargada a PNG 360x480 de 256 colores (~120 KB por póster)."""
    from PIL import Image, ImageOps

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = ImageOps.fit(img.convert("RGB"), POSTER_SIZE, Image.LANCZOS)
        img = img.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
        img.save(destination, format="PNG", optimize=True)
    return destination
