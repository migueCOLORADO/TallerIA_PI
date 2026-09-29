# Ureview — Taller 3: Integración de IA (Claude + Higgsfield + embeddings locales)

Proyecto Django del curso ST0251 (Miguel Colorado), rama `miguel-colorado` del fork de
[TallerIA_PI](https://github.com/jdmartinev/TallerIA_PI). Parte del proyecto real de los
Talleres 1 y 2 (catálogo de 148 títulos, reseñas, reacciones, login, búsqueda en vivo) y le
agrega descripciones generadas con IA, pósters ilustrados con IA y un sistema de recomendación
por embeddings. El enunciado original del curso está en [README_TALLER_ORIGINAL.md](README_TALLER_ORIGINAL.md)
y en los archivos `1_…md` a `7_…md`.

## Qué se implementó

| Punto del taller | Implementación |
|---|---|
| Campo de embeddings | `Movie.emb = BinaryField(null=True, blank=True)` (migración `0004_movie_emb`). No se tocó ningún otro campo. |
| 4. Descripciones con IA | Claude (Anthropic API) reescribe y enriquece la sinopsis de las 148 películas en español. |
| 5. Imágenes con IA | Higgsfield genera un póster ilustrado para 62 títulos (las 50 del seed curado + 12 mudas). |
| 6. Similitud | `sentence-transformers` local calcula embeddings y similitud coseno entre películas y prompts. |
| 7. Recomendación | Vista `/recommend/`: el usuario describe qué quiere ver y se muestra la película más similar + 3 alternativas. |
| Pruebas | 13 pruebas unitarias nuevas (25 en total) y una simulación Monte Carlo de 200 corridas. |

## Por qué Claude + Higgsfield + sentence-transformers (y no OpenAI / Hugging Face)

El enunciado usa la API de OpenAI (y opcionalmente el Hub de Hugging Face). **Por decisión del
estudiante** se reemplazaron los proveedores manteniendo el mismo patrón de cada punto:

- **Texto → Claude (Anthropic).** Se usa `claude-haiku-4-5`, el modelo más económico de Claude,
  suficiente para reescribir una sinopsis corta. Control de gasto: `max_tokens=150`, máximo
  1 reintento por fallo transitorio, piloto de 5 películas antes del batch completo.
- **Imágenes → Higgsfield.** Modelo `z_image` (0.15 créditos por imagen, el más barato del
  catálogo). Se usa a través del servidor MCP de Higgsfield desde Claude Code; ver
  [aux_files/README_higgsfield.md](aux_files/README_higgsfield.md) para el flujo completo.
- **Embeddings → sentence-transformers local.** Sin costo por consulta, sin API key y sin enviar
  datos a terceros. La recomendación y el Monte Carlo corren 100 % en local.

### Modelo de embeddings

Se usa `intfloat/multilingual-e5-small` (~470 MB, 384 dimensiones). Es liviano como
`all-MiniLM-L6-v2`, pero ese modelo está entrenado casi solo en inglés y aquí tanto las
sinopsis como los prompts están en español. Se compararon tres modelos locales con 10 prompts
de prueba de respuesta conocida (top-1 exacto):

| Modelo | Texto embebido | Top-1 exacto |
|---|---|---|
| `paraphrase-multilingual-MiniLM-L12-v2` | sinopsis | 4/10 |
| `paraphrase-multilingual-MiniLM-L12-v2` | título + género + sinopsis | 5/10 |
| `intfloat/multilingual-e5-small` | título + género + sinopsis | **7/10** (9/10 si se cuentan respuestas razonables fuera de la lista, p. ej. *Gertie the Dinosaur* para "dinosaurios") |
| `paraphrase-multilingual-mpnet-base-v2` (1.1 GB) | título + género + sinopsis | 8/10 |

E5 se eligió por la relación calidad/tamaño. Espera los prefijos `query: ` (prompt del usuario)
y `passage: ` (texto de la película), que se aplican en `movie/ai_utils.py`.

## Configuración

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt

# .env en la raíz (NO se versiona; .gitignore excluye .env y *.env)
# ANTHROPIC_API_KEY=sk-ant-...

python manage.py migrate
python manage.py add_movies_db      # 98 películas de movies_initial.csv
python manage.py seed_movies        # 50 títulos curados + reseñas
python manage.py add_news_db
python manage.py createsuperuser
python manage.py runserver
```

La primera vez que se calcula un embedding se descarga el modelo de Hugging Face (~470 MB);
después se carga desde la caché local sin tocar la red.

## Comandos del Taller 3

Descripciones (Claude):

```powershell
python manage.py update_descriptions                          # 1 película (patrón del taller, con break)
python aux_files/generate_descriptions_batch.py --limit 5     # piloto (gasta API)
python aux_files/generate_descriptions_batch.py               # resto del catálogo -> updated_movie_descriptions.csv
python manage.py update_movies_from_csv                       # carga el CSV en la BD
```

El CSV [updated_movie_descriptions.csv](updated_movie_descriptions.csv) ya está generado con
los 148 títulos reales (columnas `Title,Updated Description`), así que basta con
`update_movies_from_csv`. Costo real del batch: **US$0.12** (≈27 k tokens de entrada, ≈18.5 k de salida).

Pósters (Higgsfield):

```powershell
python manage.py update_images                 # 1 película (patrón del taller, con break)
python manage.py update_images_from_folder     # asigna media/movie/images/m_<title_slug>.png a cada película
```

Los 62 pósters ya están en `media/movie/images/`. Costo real: **11.4 créditos** de Higgsfield
(incluye generaciones descartadas y reintentos).

Embeddings y recomendación (local):

```powershell
python manage.py movie_embeddings              # embedding de las 148 películas -> campo emb
python manage.py movie_similarities            # Interstellar vs The Godfather + prompt "película de ciencia ficción"
python manage.py movie_similarities --movie1 "The Matrix" --movie2 "Inception" --prompt "robots y realidad virtual"
python manage.py show_random_embedding         # embedding de una película al azar
python manage.py montecarlo_recommendation_eval   # 200 simulaciones -> montecarlo_results.txt
```

Vista web: `http://127.0.0.1:8000/recommend/` (ítem **Recommend** del navbar).

## Sistema de recomendación

1. `movie_embeddings` guarda en `emb` el embedding (float32, 384 valores, normalizado) de
   `"<título>. <género>. <sinopsis>"`.
2. En `/recommend/` (POST) se calcula el embedding del prompt, se compara por similitud coseno
   contra todas las películas con `emb` y se muestra la de mayor similitud, su puntaje y 3 alternativas.
3. Si no hay películas con embedding o el prompt está vacío, la vista muestra un mensaje en lugar de fallar.

El template `movie/templates/movie/recommend.html` extiende `base.html` (mismo navbar, footer y
tema oscuro) y usa el grid de Bootstrap (`row-cols-1 row-cols-sm-2 row-cols-md-3`) como el resto
del catálogo. Se verificó en 1366 px y 375 px: sin scroll horizontal, formulario y resultado apilados en móvil.

## Resultados Monte Carlo

`python manage.py montecarlo_recommendation_eval` genera 200 prompts aleatorios combinando
géneros, temas y tonos del catálogo, y verifica cada recomendación. Resultado (semilla 42,
detalle en [montecarlo_results.txt](montecarlo_results.txt)):

| Métrica | Valor |
|---|---|
| Éxito (película válida, similitud en [-1, 1]) | **200/200 (100 %)** |
| Similitud promedio / mínima / máxima | 0.8516 / 0.8178 / 0.8985 |
| Tiempo de respuesta promedio (embedding + búsqueda) | **26.9 ms** |
| Mediana / p95 / máximo | 26.4 ms / 34.3 ms / 154.2 ms |
| Películas distintas recomendadas | 58 de 148 |
| Carga del modelo (una vez por proceso, excluida) | ~24 s |

Las similitudes de E5 se concentran en un rango alto (0.8–0.9) por cómo está entrenado el
modelo; lo que importa es el orden relativo entre películas, no el valor absoluto.

## Pruebas

```powershell
python manage.py test
```

25 pruebas, todas pasan. Las 13 nuevas (`movie/tests.py`) cubren:

- `Movie.emb` acepta binario y se lee de vuelta con `np.frombuffer`.
- Similitud coseno: vectores idénticos → 1.0, ortogonales → 0.0, opuestos → -1.0, vector cero sin división por cero.
- `update_movies_from_csv` actualiza `synopsis` desde un CSV de prueba y reporta títulos no encontrados.
- `update_images_from_folder` asigna `poster` desde archivos de prueba y no toca películas sin archivo.
- Vista `recommend`: GET 200 con el template correcto; POST con prompt válido retorna la película
  esperada; prompt vacío muestra un error; sin películas con embedding no falla y muestra un mensaje;
  el navbar incluye el enlace.

Las pruebas de la vista usan el modelo local real (no llaman a ninguna API externa).

## Capturas del Taller 3

Van en [capturas_taller3/](capturas_taller3/); la lista de las que hay que tomar está en
[capturas_taller3/README.md](capturas_taller3/README.md).

---

# Taller 2 (Django + Bootstrap)

Guía completa de ejecución y pruebas: [GUIA_EJECUCION_Y_PRUEBAS.md](GUIA_EJECUCION_Y_PRUEBAS.md).

1. **Repositorio / rama original**: https://github.com/migueCOLORADO/PupiGo/tree/Miguel-Colorado-Talleres

2. **≥10 películas en Cards de Bootstrap (genre y year visibles) + navbar con imagen**
   ![Catálogo con Cards Bootstrap](capturas/Taller%202/punto1.png)
   ![Catálogo con Cards Bootstrap (cont.)](capturas/Taller%202/punto1.1.png)
   ![Catálogo con Cards Bootstrap (cont.)](capturas/Taller%202/punto1.2.png)
   ![Catálogo con Cards Bootstrap (cont.)](capturas/Taller%202/punto1.3.png)

3. **Mismo listado en ventana angosta (responsive)**
   ![Catálogo responsive](capturas/Taller%202/punto2.png)

4. **News en Horizontal Cards**
   ![News horizontal cards](capturas/Taller%202/punto3.png)

5. **Gráfica de películas por año**
   ![Gráfica por año](capturas/Taller%202/punto4.png)

6. **Gráfica de películas por género**
   ![Gráfica por género](capturas/Taller%202/punto5.png)
