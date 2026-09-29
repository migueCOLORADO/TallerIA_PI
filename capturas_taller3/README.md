# Capturas del Taller 3 (tomarlas manualmente)

Levanta el servidor (`python manage.py runserver`) y guarda cada captura en esta carpeta con el
nombre indicado.

| # | Archivo | Qué mostrar | Cómo llegar |
|---|---|---|---|
| 1 | `1_admin_descripcion.png` | Admin con la sinopsis enriquecida de la primera película (*Carmencita*) | `/admin/movie/movie/` → *Carmencita* (necesitas un superusuario: `python manage.py createsuperuser`) |
| 2 | `2_peliculas_imagenes.png` | Listado con pósters generados con Higgsfield | `/movies/?genero=Crimen` o `/` (catálogo completo) |
| 3 | `3_movie_similarities.png` | Consola con las 2 películas, el prompt y las similitudes | `python manage.py movie_similarities` |
| 4 | `4_embedding_consola.png` | Consola con el embedding de una película | `python manage.py show_random_embedding` |
| 5 | `5_recommend.png` | `/recommend/` con un prompt escrito y la película recomendada | `/recommend/` → escribe, p. ej., "historia de mafia y traición familiar" → **Recomendar** |
| 6 (opcional) | `6_recommend_movil.png` | `/recommend/` en ventana angosta | DevTools → modo dispositivo, 375 px |
| 7 (opcional) | `7_montecarlo.png` | Consola del Monte Carlo | `python manage.py montecarlo_recommendation_eval` |
