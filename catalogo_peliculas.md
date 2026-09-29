# Catálogo de películas/series (muestra representativa)

Consultado vía Django ORM (`manage.py shell`) directo de la base de datos.
Origen distinguido comparando `title` contra la lista hardcodeada en
`movie/management/commands/seed_movies.py` (50 títulos) vs el resto,
cargado por `add_movies_db.py` desde `movies_initial.csv` (98 títulos).

## Seed curado original (50 en DB, 10 mostrados)

| title | content_type | release_year | genre |
|---|---|---|---|
| Gladiator | movie | 2000 | Acción |
| Avatar: The Last Airbender | series | 2005 | Animación |
| Coco | movie | 2017 | Animación |
| Jurassic Park | movie | 1993 | Aventura |
| Black Mirror | series | 2011 | Ciencia Ficción |
| Her | movie | 2013 | Ciencia Ficción |
| Friends | series | 1994 | Comedia |
| Superbad | movie | 2007 | Comedia |
| Fargo | series | 2014 | Crimen |
| No Country for Old Men | movie | 2007 | Crimen |

## Cargados desde movies_initial.csv (98 en DB, 10 mostrados)

| title | content_type | release_year | genre |
|---|---|---|---|
| The Last Days of Pompeii | movie | 1913 | Adventure, Drama |
| Pauvre Pierrot | movie | 1892 | Animation, Comedy, Short |
| The Story of the Kelly Gang | movie | 1906 | Biography, Crime, Drama |
| Her Crowning Glory | movie | 1911 | Comedy, Short |
| Fantomas | movie | 1913 | Crime, Drama |
| Baby's Dinner | movie | 1895 | Documentary, Short |
| Fantomas Against Fantomas | movie | 1914 | Drama |
| Cinderella | movie | 1914 | Fantasy, Drama |
| A Turn of the Century Illusionist | movie | 1899 | Short |
| Dante's Inferno | movie | 1911 | Adventure, Drama, Fantasy |
