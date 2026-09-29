"""Paso 1 de los pósters: exporta el prompt Higgsfield de cada película.

    python aux_files/build_poster_prompts.py

Salida: aux_files/higgsfield_prompts.json ([{index, title, filename, prompt}]).
El agente (Claude Code + MCP de Higgsfield) envía estos prompts en lotes con
generate_image_batch y registra cada job en aux_files/higgsfield_posters.json.
"""
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviereviews.settings")

import django  # noqa: E402

django.setup()

from movie.models import Movie  # noqa: E402
from movie.poster_utils import build_poster_prompt, poster_filename  # noqa: E402

OUTPUT = BASE_DIR / "aux_files" / "higgsfield_prompts.json"

items = [
    {"index": i, "title": m.title, "filename": poster_filename(m.title), "prompt": build_poster_prompt(m)}
    for i, m in enumerate(Movie.objects.all().order_by("pk"))
]
OUTPUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(items)} prompts -> {OUTPUT}")
