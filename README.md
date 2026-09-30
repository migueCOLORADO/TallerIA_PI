# Ureview — Taller 3: Integración de IA | Proyecto Integrador 1 (PI1)

## Tabla de contenido
1. [Descripción](#descripción)
   1. [Contexto](#contexto)
   2. [Qué se implementó](#qué-se-implementó)
2. [Decisiones técnicas](#decisiones-técnicas)
   1. [Texto: Claude en vez de OpenAI](#texto-claude-en-vez-de-openai)
   2. [Imágenes: Higgsfield en vez de DALL-E](#imágenes-higgsfield-en-vez-de-dall-e)
   3. [Embeddings: sentence-transformers en vez de OpenAI](#embeddings-sentence-transformers-en-vez-de-openai)
   4. [Sistema de recomendación](#sistema-de-recomendación)
3. [Cómo ejecutar](#cómo-ejecutar)
   1. [Requisitos](#requisitos)
   2. [Instalación (Windows PowerShell)](#instalación-windows-powershell)
   3. [Capturas](#capturas)
   4. [Entregable en PDF](#entregable-en-pdf)
   5. [Video de demostración](#video-de-demostración)
4. [Comandos](#comandos)
5. [Resultados](#resultados)
   1. [Gasto real](#gasto-real)
   2. [Comparación de modelos de embeddings](#comparación-de-modelos-de-embeddings)
   3. [Monte Carlo](#monte-carlo)
   4. [Pruebas unitarias](#pruebas-unitarias)
6. [Solución de problemas](#solución-de-problemas)
7. [Autor](#autor)

## Descripción

### Contexto

Taller 3 del curso ST0251, rama `miguel-colorado` del fork de [TallerIA_PI](https://github.com/jdmartinev/TallerIA_PI). En lugar del proyecto genérico del curso (`DjangoProjectBase/`, eliminado), el taller corre sobre el proyecto real de los Talleres 1 y 2 (Ureview, rama `Miguel-Colorado-Talleres` del repo [PupiGo](https://github.com/migueCOLORADO/PupiGo/tree/Miguel-Colorado-Talleres)): catálogo de 148 títulos (50 del seed curado + 98 de `movies_initial.csv`), reseñas, reacciones, login y búsqueda en vivo. El enunciado original está en [README_TALLER_ORIGINAL.md](README_TALLER_ORIGINAL.md) y en `1_…md` a `7_…md`; la guía y capturas de los Talleres 1–2 siguen en [GUIA_EJECUCION_Y_PRUEBAS.md](GUIA_EJECUCION_Y_PRUEBAS.md) y [capturas/](capturas/).

### Qué se implementó

| Punto del taller | Implementación |
|---|---|
| Campo de embeddings | `Movie.emb = BinaryField(null=True, blank=True)` (migración `0004_movie_emb`). No se tocó ningún otro campo. |
| 4. Descripciones con IA | Claude reescribe y enriquece en español la sinopsis de las 148 películas. |
| 5. Imágenes con IA | Higgsfield genera un póster ilustrado para 62 títulos (las 50 del seed + 12 mudas). |
| 6. Similitud | `sentence-transformers` local calcula embeddings y similitud coseno entre películas y prompts. |
| 7. Recomendación | Vista `/recommend/`: el usuario describe qué quiere ver; se muestra la película más similar + 3 alternativas. |
| Pruebas | 13 pruebas unitarias nuevas (25 en total) y simulación Monte Carlo de 200 corridas. |

<details>
<summary><b>Taller 1</b></summary>

![Home](capturas/Taller%201/home.png)
![About](capturas/Taller%201/about.png)
![Listado de películas](capturas/Taller%201/listadoPeliculas.png)
![Películas con patrón](capturas/Taller%201/peliculasPatron.png)

</details>

<details>
<summary><b>Taller 2</b></summary>

Guía: [GUIA_EJECUCION_Y_PRUEBAS.md](GUIA_EJECUCION_Y_PRUEBAS.md) · Rama original: https://github.com/migueCOLORADO/PupiGo/tree/Miguel-Colorado-Talleres

1. **≥10 películas en Cards de Bootstrap + navbar con imagen**
   ![Cards](capturas/Taller%202/punto1.png)
   ![Cards (cont.)](capturas/Taller%202/punto1.1.png)
   ![Cards (cont.)](capturas/Taller%202/punto1.2.png)
   ![Cards (cont.)](capturas/Taller%202/punto1.3.png)
2. **Listado responsive** ![Responsive](capturas/Taller%202/punto2.png)
3. **News en Horizontal Cards** ![News](capturas/Taller%202/punto3.png)
4. **Gráfica por año** ![Por año](capturas/Taller%202/punto4.png)
5. **Gráfica por género** ![Por género](capturas/Taller%202/punto5.png)

</details>

## Decisiones técnicas

El enunciado usa OpenAI (y opcionalmente el Hub de Hugging Face). **Por decisión del estudiante** se reemplazaron los proveedores manteniendo el mismo patrón de cada punto (comando con `break` para 1 película + proceso masivo aparte).

### Texto: Claude en vez de OpenAI

- Modelo `claude-haiku-4-5`, el más económico de Claude, suficiente para reescribir una sinopsis corta.
- Control de gasto: `max_tokens=150`, máximo 1 reintento por fallo transitorio, piloto de 5 películas antes del lote; si una película falla se registra y se sigue.
- El lote (`aux_files/generate_descriptions_batch.py`) es reanudable: los títulos ya presentes en el CSV no se vuelven a pedir.
- La key se lee de `.env` en la raíz con `python-dotenv`; `.env` y `*.env` están en `.gitignore`.

### Imágenes: Higgsfield en vez de DALL-E

Higgsfield se usó a través de su **servidor MCP** (disponible para el agente en Claude Code), no como API REST que un comando `manage.py` pueda llamar por su cuenta. Por eso el flujo se partió en pasos:

| Paso | Quién lo ejecuta | Salida |
|---|---|---|
| 1. Prompts | `python aux_files/build_poster_prompts.py` | `aux_files/higgsfield_prompts.json` |
| 2. Generación | Agente con el MCP de Higgsfield (`generate_image_batch` + `jobs_wait`, lotes de ≤12) | `aux_files/higgsfield_jobs.txt` (`<index> <job_id> <url>`) |
| 3. Manifiesto | `python aux_files/build_higgsfield_manifest.py` | `aux_files/higgsfield_posters.json` |
| 4. Descarga | `python aux_files/download_higgsfield_posters.py` | `media/movie/images/m_<title_slug>.png` |
| 5. BD | `python manage.py update_images_from_folder` | campo `poster` |

- Modelo `z_image` (0.15 créditos por imagen, el más barato del catálogo), relación 3:4. La salida (1536×2048) se reduce a 360×480 y se cuantiza a PNG de 256 colores (~120 KB por póster).
- El título **no** va en el prompt: cuando aparecía, el modelo lo escribía (mal) sobre la imagen.
- Piloto de 10 títulos del seed antes del resto. Las 86 películas mudas restantes conservan su póster original (poco relevantes para la demo).
- Detalle de reintentos en [aux_files/README_higgsfield.md](aux_files/README_higgsfield.md).

### Embeddings: sentence-transformers en vez de OpenAI

- Modelo local `intfloat/multilingual-e5-small` (~470 MB, 384 dimensiones): sin costo por consulta, sin API key y sin enviar datos a terceros.
- No se usó `all-MiniLM-L6-v2` porque está entrenado casi solo en inglés y las sinopsis y prompts están en español (ver [comparación](#comparación-de-modelos-de-embeddings)).
- E5 espera los prefijos `query: ` (prompt del usuario) y `passage: ` (texto de la película), aplicados en `movie/ai_utils.py`.
- El modelo se descarga una sola vez y luego se carga desde la caché local.

### Sistema de recomendación

1. `movie_embeddings` guarda en `emb` el embedding (float32, 384 valores, normalizado) de `"<título>. <género>. <sinopsis>"`.
2. En `/recommend/` (POST) se calcula el embedding del prompt, se compara por similitud coseno contra todas las películas con `emb` y se muestra la de mayor similitud, su puntaje y 3 alternativas.
3. Prompt vacío o ninguna película con embedding → mensaje en pantalla, sin error.
4. Todo es local: ninguna llamada a APIs externas por request.
5. `recommend.html` extiende `base.html` (navbar, footer, tema oscuro) y usa el grid de Bootstrap (`row-cols-1 row-cols-sm-2 row-cols-md-3`). Verificado en 1366 px y 375 px: sin scroll horizontal, formulario y resultado apilados en móvil.

## Cómo ejecutar

### Requisitos

- Python 3.13
- `ANTHROPIC_API_KEY` (solo para regenerar descripciones; el CSV ya está generado)
- ~470 MB libres para el modelo de embeddings (descarga automática la primera vez)

### Instalación (Windows PowerShell)

```powershell
# 1. Clonar la rama
git clone -b miguel-colorado https://github.com/migueCOLORADO/TallerIA_PI.git
cd TallerIA_PI

# 2. Entorno virtual y dependencias
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. .env en la raíz (no se versiona)
# ANTHROPIC_API_KEY=sk-ant-...

# 4. Migraciones y datos
python manage.py migrate
python manage.py add_movies_db      # 98 películas de movies_initial.csv
python manage.py seed_movies        # 50 títulos curados + reseñas
python manage.py add_news_db

# 5. Contenido de IA ya generado (sin gastar API)
python manage.py update_movies_from_csv
python manage.py update_images_from_folder
python manage.py movie_embeddings

# 6. Superusuario y servidor
python manage.py createsuperuser
python manage.py runserver
```

URLs: `/`, `/movies/`, `/series/`, `/news/`, `/statistics/`, `/recommend/`, `/admin/`.

### Capturas

1. **`update_descriptions.py`** (`python manage.py update_descriptions`)

   ![Terminal de update_descriptions](<capturas/Taller 3/1a_update_descriptions_terminal.png>)
   ![Admin con la sinopsis enriquecida](<capturas/Taller 3/1b_admin_synopsis.png>)

2. **`update_movies_from_csv`** (`python manage.py update_movies_from_csv`)

   ![Terminal de update_movies_from_csv](<capturas/Taller 3/2_update_movies_from_csv.png>)

3. **`update_images.py`, primera película** (`python manage.py update_images`)

   ![Terminal de update_images](<capturas/Taller 3/3a_update_images_terminal.png>)
   ![Admin con el póster actualizado](<capturas/Taller 3/3b_admin_poster.png>)

4. **`update_images_from_folder`** (`python manage.py update_images_from_folder`)

   ![Terminal de update_images_from_folder](<capturas/Taller 3/4_update_images_from_folder.png>)

5. **`movie_embeddings` + `movie_similarities`**

   ![Terminal de movie_embeddings](<capturas/Taller 3/5a_movie_embeddings.png>)
   ![Terminal de movie_similarities](<capturas/Taller 3/5b_movie_similarities.png>)

6. **`show_random_embedding`** (`python manage.py show_random_embedding`)

   ![Terminal de show_random_embedding](<capturas/Taller 3/6_show_random_embedding.png>)

### Entregable en PDF

Documento con evidencia completa (links de repositorio, comando ejecutado y captura por cada requerimiento del taller): [Taller3_TallerIA_PI_Entregable.pdf](Taller3_TallerIA_PI_Entregable.pdf).

### Video de demostración

Recorrido por la aplicación y la ejecución de los comandos del taller: https://youtu.be/01Ss10SWZ38

## Comandos

| Comando | Qué hace | ¿Gasta API? |
|---|---|---|
| `python manage.py update_descriptions` | Enriquece con Claude la sinopsis de la **primera** película (patrón del taller, con `break`) | Sí (1 llamada) |
| `python aux_files/generate_descriptions_batch.py [--limit N] [--titles "A\|B"]` | Lote de Claude → `updated_movie_descriptions.csv` (`Title,Updated Description`) | Sí |
| `python manage.py update_movies_from_csv [--csv RUTA]` | Carga el CSV en `synopsis` y reporta títulos no encontrados | No |
| `python manage.py update_images` | Descarga el póster Higgsfield de la **primera** película y actualiza `poster` (con `break`) | No (usa el job ya generado) |
| `python manage.py update_images_from_folder` | Asigna `media/movie/images/m_<title_slug>.png` a cada película | No |
| `python manage.py movie_similarities [--movie1 --movie2 --prompt]` | Similitud coseno entre 2 películas y un prompt (por defecto Interstellar vs The Godfather, "película de ciencia ficción") | No |
| `python manage.py movie_embeddings` | Embedding de las 148 películas → campo `emb` | No |
| `python manage.py show_random_embedding [--n 10]` | Muestra el embedding de una película al azar | No |
| `python manage.py montecarlo_recommendation_eval [--n 200 --seed 42]` | Simulación Monte Carlo → `montecarlo_results.txt` | No |

## Resultados

### Gasto real

| Proveedor | Detalle | Costo |
|---|---|---|
| Claude (Haiku 4.5) | 148 sinopsis (piloto 5 + lote 143), 0 fallidas, 0 truncadas; ≈27 k tokens de entrada, ≈18.5 k de salida | **US$0.12** |
| Higgsfield (`z_image`) | 76 generaciones × 0.15 (62 pósters finales + descartados y reintentos) | **11.4 créditos** |
| sentence-transformers | Local | $0 |

### Comparación de modelos de embeddings

10 prompts de prueba con respuesta conocida (acierto en 1.er lugar):

| Modelo | Texto embebido | Acierto en 1.er lugar |
|---|---|---|
| `paraphrase-multilingual-MiniLM-L12-v2` | sinopsis | 4/10 |
| `paraphrase-multilingual-MiniLM-L12-v2` | título + género + sinopsis | 5/10 |
| `intfloat/multilingual-e5-small` | título + género + sinopsis | **7/10** (9/10 contando respuestas razonables fuera de la lista, p. ej. *Gertie the Dinosaur* para "dinosaurios") |
| `paraphrase-multilingual-mpnet-base-v2` (1.1 GB) | título + género + sinopsis | 8/10 |

E5-small se eligió por la relación calidad/tamaño.

### Monte Carlo

200 prompts aleatorios (géneros, temas y tonos del catálogo), semilla 42; detalle en [montecarlo_results.txt](montecarlo_results.txt):

| Métrica | Valor |
|---|---|
| Éxito (película válida, similitud en [-1, 1]) | **200/200 (100 %)** |
| Similitud promedio / mínima / máxima | 0.8516 / 0.8178 / 0.8985 |
| Tiempo promedio (embedding + búsqueda) | **26.9 ms** |
| Mediana / p95 / máximo | 26.4 ms / 34.3 ms / 154.2 ms |
| Películas distintas recomendadas | 58 de 148 |
| Carga del modelo (una vez, excluida) | ~24 s |

Las similitudes de E5 se concentran en un rango alto (0.8–0.9) por cómo está entrenado el modelo; lo que importa es el orden relativo.

### Pruebas unitarias

`python manage.py test` → **25 pruebas, todas pasan**. Las 13 nuevas (`movie/tests.py`):

- `Movie.emb` acepta binario y se lee con `np.frombuffer`.
- Similitud coseno: idénticos → 1.0, ortogonales → 0.0, opuestos → -1.0, vector cero sin división por cero.
- `update_movies_from_csv` actualiza `synopsis` y reporta títulos no encontrados.
- `update_images_from_folder` asigna `poster` y no toca películas sin archivo.
- Vista `recommend`: GET 200 con el template correcto; POST válido retorna la película esperada; prompt vacío → error; sin embeddings → mensaje sin fallar; navbar con enlace.

Las pruebas de la vista usan el modelo local real (sin APIs externas).

## Solución de problemas

| Problema | Solución |
|---|---|
| PowerShell bloquea `Activate.ps1` | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `ANTHROPIC_API_KEY no está definida` | Crear `.env` en la raíz con `ANTHROPIC_API_KEY=...` |
| Primera ejecución de embeddings lenta / aviso de symlinks en Windows | Es la descarga única del modelo (~470 MB); el aviso es inofensivo |
| `/recommend/` muestra "Cargando el modelo de IA…" justo después de iniciar el servidor | El modelo se precarga en segundo plano (~25–40 s en Windows); la página reintenta sola y muestra el resultado al terminar |
| Editar una película con póster IA desde `/admin/` rechaza el campo `poster` | `poster` es `URLField` y guarda rutas relativas (`/media/movie/images/...`); se muestra bien en todas las vistas. No se cambió el campo para no modificar el modelo más allá de `emb` |
| Higgsfield marca un prompt como NSFW o devuelve imagen en negro | Reescribir el prompt (ver `PROMPT_OVERRIDES` en `aux_files/build_higgsfield_manifest.py`) |
| Higgsfield responde `429 rate_limit_reached` | Enviar los lotes de forma secuencial, no en paralelo |
| `git push` falla con "unexpected disconnect" | `git config http.postBuffer 524288000` |

## Autor

Miguel A. Colorado Castaño

Curso: ST0251 Proyecto Integrador 1 (PI1)
Profesor: Wilmer Alberto Gil Moreno
Universidad: Universidad EAFIT | Escuela de Ciencias Aplicadas e Ingeniería
Programa: Ingeniería de Sistemas
Año: 2026-2
