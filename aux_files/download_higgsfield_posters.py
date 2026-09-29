"""Paso 3 de los pósters: descarga las imágenes generadas con Higgsfield.

    python aux_files/download_higgsfield_posters.py

Lee aux_files/higgsfield_posters.json (title, filename, job_id, model, url),
descarga cada resultado y lo guarda como PNG 360x480 en media/movie/images/m_<title_slug>.png.
Luego se asignan a las películas con: python manage.py update_images_from_folder
"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviereviews.settings")

import django  # noqa: E402

django.setup()

import requests  # noqa: E402

from movie.poster_utils import MANIFEST_PATH, images_dir, save_png  # noqa: E402


def download(item):
    destination = images_dir() / item["filename"]
    if destination.exists():
        return item["title"], "ya existe"
    response = requests.get(item["url"], timeout=120)
    response.raise_for_status()
    save_png(response.content, destination)
    return item["title"], "ok"


def main():
    items = [i for i in json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) if i.get("url")]
    errors = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(download, item) for item in items]
        for item, future in zip(items, futures):
            try:
                title, status = future.result()
                print(f"{status:9} {title}")
            except Exception as e:
                errors += 1
                print(f"ERROR     {item['title']}: {e}")
    print(f"Descargadas/presentes: {len(items) - errors} de {len(items)} en {images_dir()}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
