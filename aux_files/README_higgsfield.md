# Pósters con Higgsfield — flujo y decisiones

## Por qué la generación no ocurre dentro de un comando Django

Higgsfield se usó a través de su **servidor MCP**, que está disponible para el agente
(Claude Code) pero no como una API REST con key que un comando `manage.py` pueda
llamar por su cuenta. Por eso el pipeline se partió en pasos:

| Paso | Quién lo ejecuta | Archivo | Salida |
|---|---|---|---|
| 1. Prompts | `python aux_files/build_poster_prompts.py` | `movie/poster_utils.py::build_poster_prompt` | `aux_files/higgsfield_prompts.json` |
| 2. Generación | Agente, con el MCP de Higgsfield (`generate_image_batch` + `jobs_wait`, lotes de ≤12) | — | una línea `<index> <job_id> <url>` por job en `aux_files/higgsfield_jobs.txt` |
| 3. Manifiesto | `python aux_files/build_higgsfield_manifest.py` | — | `aux_files/higgsfield_posters.json` (título, archivo, modelo, job, url, prompt) |
| 4. Descarga | `python aux_files/download_higgsfield_posters.py` | `movie/poster_utils.py::save_png` | `media/movie/images/m_<title_slug>.png` |
| 5. BD | `python manage.py update_images_from_folder` | — | campo `poster` de cada película |

`python manage.py update_images` reproduce el patrón del taller para **una sola película**
(con `break`): toma el job de Higgsfield de la primera película del manifiesto, descarga la
imagen en `media/movie/images/` y actualiza `poster`.

## Parámetros y control de gasto

- Modelo: `z_image` (el más económico del catálogo de Higgsfield: 0.15 créditos por imagen),
  relación 3:4. La salida (1536×2048) se reduce a 360×480 y se cuantiza a PNG de 256 colores
  (~120 KB por póster) para no inflar el repositorio.
- El título **no** va en el prompt: cuando aparecía, el modelo lo escribía (mal) sobre la imagen.
- Piloto de 10 títulos del seed curado antes del resto (decisión validada con el usuario).

## Qué películas tienen póster generado (62 de 148)

- **Las 50 del seed curado** (películas y series conocidas): todas.
- **12 películas mudas (1892–1896)** del CSV del curso: se generaron antes de fijar la regla de
  gasto; se conservaron porque ya estaban pagadas.
- Las 86 películas mudas restantes conservan su póster original (URL de IMDb o placeholder);
  son poco relevantes para la demo y se decidió no gastar créditos en ellas.

## Reintentos

| Película | Motivo | Solución |
|---|---|---|
| The Sea (1895) | filtro NSFW (niños saltando al mar) | prompt reescrito: muelle y bañistas adultos |
| Toy Story (1995) | falso positivo del filtro NSFW | prompt reescrito describiendo los juguetes |
| Fight Club (1999) | imagen devuelta en negro | prompt reescrito |
| Breaking Bad (2008) | letras dentro de la imagen | prompt reescrito |
| Get Out (2017) | glifo suelto en la imagen | regenerado con el mismo prompt |
| Primer lote (12 mudas) | incluía el título escrito | se quitó el título del prompt y se regeneró |

Costo total: **11.4 créditos** (76 generaciones × 0.15, incluidas las descartadas).
