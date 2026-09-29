"""Paso 2 de los pósters: consolida los jobs de Higgsfield en aux_files/higgsfield_posters.json.

    python aux_files/build_higgsfield_manifest.py

Entrada: aux_files/higgsfield_prompts.json (paso 1) y aux_files/higgsfield_jobs.txt,
donde el agente registra una línea "<index> <job_id> <result_url>" por cada job
completado con el MCP de Higgsfield (generate_image_batch + jobs_wait).
"""
import json
from pathlib import Path

AUX = Path(__file__).resolve().parent
MODEL = "z_image"

# "Get Out" (111) se generó dos veces (la primera traía un glifo suelto); el manifiesto
# se queda con la última línea registrada para cada película.
# Prompts reescritos a mano cuando el filtro de contenido de Higgsfield rechazó el original
PROMPT_OVERRIDES = {
    8: (  # "The Sea" (1895): el original (niños saltando al mar) fue marcado como NSFW
        "Textless cinematic key art illustration for a Documentary, Short film from 1895. "
        "Scene: A wooden pier on a sunny Mediterranean coast at the end of the 19th century, "
        "big waves splashing against the posts, swimmers in vintage striped bathing costumes "
        "diving into the blue sea. Painterly digital illustration, dramatic lighting, rich colors, "
        "strong central composition. Pure artwork only: no typography, no lettering, no captions, "
        "no logos, no watermark."
    ),
    110: (  # "Toy Story" (1995): falso positivo del filtro NSFW con el prompt original
        "Textless cinematic key art illustration for a Animación film from 1995. "
        "Scene: A pull-string cowboy doll and a shiny space ranger action figure come to life "
        "on a bedroom floor full of toys, rivals facing each other under a sky-blue wallpaper "
        "with clouds. Painterly digital illustration, dramatic lighting, rich colors, strong "
        "central composition. Pure artwork only: no typography, no lettering, no captions, "
        "no logos, no watermark."
    ),
    107: (  # "Fight Club" (1999): la primera generación llegó en negro (censurada)
        "Textless cinematic key art illustration for a Drama film from 1999. Scene: A sleepless "
        "office worker in a wrinkled shirt stands in a dim basement lit by a single bare bulb, his "
        "confident alter ego in a red leather jacket smirking behind him, a pink soap bar on a crate. "
        "Painterly digital illustration, dramatic lighting, rich colors, strong central composition. "
        "Original characters, no real actors' likeness. Pure artwork only: no typography, no "
        "lettering, no captions, no logos, no watermark."
    ),
    128: (  # "Breaking Bad" (2008): la primera generación incluía letras
        "Textless cinematic key art illustration for a Drama TV series from 2008. Scene: A mild "
        "chemistry teacher in a yellow hazmat suit and gas mask stands beside an old RV in the New "
        "Mexico desert at sunset, glass lab flasks glowing blue. Painterly digital illustration, "
        "dramatic lighting, rich colors, strong central composition. Original characters, no real "
        "actors' likeness. Pure artwork only: no typography, no lettering, no captions, no logos, "
        "no watermark, no periodic table symbols."
    ),
}

prompts = {p["index"]: p for p in json.loads((AUX / "higgsfield_prompts.json").read_text(encoding="utf-8"))}
manifest = {}
for line in (AUX / "higgsfield_jobs.txt").read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    index, job_id, url = line.split()
    item = prompts[int(index)]
    manifest[item["title"]] = {
        "index": item["index"],
        "title": item["title"],
        "filename": item["filename"],
        "model": MODEL,
        "job_id": job_id,
        "url": url,
        "prompt": PROMPT_OVERRIDES.get(item["index"], item["prompt"]),
    }

items = sorted(manifest.values(), key=lambda i: i["index"])
(AUX / "higgsfield_posters.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(items)} pósters registrados -> aux_files/higgsfield_posters.json")
