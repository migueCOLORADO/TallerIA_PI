"""Descarga y reemplaza los 4 posters con texto/glifos residuales detectados.
Ejecutar una vez desde la raiz del proyecto: python aux_files/fix_4_posters.py
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviereviews.settings")

import django  # noqa: E402

django.setup()

import requests  # noqa: E402

from movie.poster_utils import images_dir, save_png  # noqa: E402

FIXES = {
    "m_better-call-saul.png": "https://d8j0ntlcm91z4.cloudfront.net/user_36FLppB0Qkvwiaj6YDqxtfThWsb/hf_20260929_053821_19fd32a6-da4c-4f2c-bcf9-d4e0517c571b.png",
    "m_money-heist.png": "https://d2ol7oe51mr4n9.cloudfront.net/user_36FLppB0Qkvwiaj6YDqxtfThWsb/ed6f30fa-6d39-4f78-b001-b876ea4887b9.png",
    "m_employees-leaving-the-lumire-factory.png": "https://d2ol7oe51mr4n9.cloudfront.net/user_36FLppB0Qkvwiaj6YDqxtfThWsb/79bcfe36-9343-4acd-a72c-bb842dde764d.png",
    "m_the-office.png": "https://d2ol7oe51mr4n9.cloudfront.net/user_36FLppB0Qkvwiaj6YDqxtfThWsb/32e30e12-bcc0-4b29-aa29-20718b2cb6d7.png",
}

if __name__ == "__main__":
    folder = images_dir()
    folder.mkdir(parents=True, exist_ok=True)
    for filename, url in FIXES.items():
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        save_png(resp.content, folder / filename)
        print(f"OK {filename}")
