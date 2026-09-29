# Guía de ejecución y pruebas — Taller 2 (Ureview)

## 1. Ejecución local desde cero (Windows / PowerShell)

Ejecutar desde la carpeta `Talleres-MiguelColorado`.

```powershell
# 1. Crear y activar el entorno virtual (si venv/ no existe)
python -m venv venv
venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar y aplicar migraciones
python manage.py makemigrations --check --dry-run
python manage.py migrate

# 4. Cargar datos (orden importa: primero movies, luego news)
python manage.py add_movies_db
python manage.py seed_movies
python manage.py add_news_db

# 5. Crear superusuario (si no existe, para entrar a /admin/)
python manage.py createsuperuser

# 6. Levantar el servidor
python manage.py runserver
```

Si PowerShell bloquea `Activate.ps1` por política de ejecución:
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` antes del paso 1.

URLs clave una vez el servidor está arriba (`http://127.0.0.1:8000/`):

| Página | URL |
|---|---|
| Home | `/` |
| News | `/news/` |
| Statistics | `/statistics/` |
| Signup | `/signup/?email=test@example.com` |
| Admin | `/admin/` |

## 2. Checklist de pruebas manuales

| # | Funcionalidad | URL | Qué debe verse | Señal de que algo falló |
|---|---|---|---|---|
| 1 | Home — catálogo | `/` | Cards Bootstrap con poster, título, synopsis, género y año; hero arriba con carrusel | Cards vacías, sin poster, o página en blanco |
| 2 | Home — responsive | `/` (ventana < 768px) | Cards en 1 columna, sin scroll horizontal | Cards cortadas o barra de scroll horizontal en el body |
| 3 | News | `/news/` | 5 horizontal cards con headline, body y date (`text-muted`) de Fake.csv | Menos de 5 noticias, o texto de ejemplo genérico en vez de noticias reales |
| 4 | Statistics | `/statistics/` | Dos gráficas PNG (por año, por género) | Imagen rota (`alt` text visible) o error 500 |
| 5 | Navbar | cualquier página | Home, Movies, Series, About, News, Statistics, Sign Up, Iniciar sesión/Cerrar sesión — todos navegan sin 404 | Algún link da 404 o `NoReverseMatch` |
| 6 | Signup | `/signup/?email=correo@test.com` | "Added correo@test.com to mailing list" + botón Home | Email no aparece, o error 500 |
| 7 | Admin — Movie | `/admin/movie/movie/` (login previo) | Lista de películas, se puede abrir/editar una | 403/404, o no aparece el modelo |
| 8 | Admin — News | `/admin/news/news/` | Lista de noticias, se puede abrir/editar una | 403/404, o no aparece el modelo |
| 9 | Pósters reales | `/movies/?genero=Acción` | Gladiator con poster real (no placeholder gris) | Gladiator, Coco, Her, etc. muestran placeholder |

## 3. Pruebas unitarias de Django

Archivos ya creados y verificados (`python manage.py test movie news` → 12 tests, OK):

**`movie/tests.py`**
```python
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Movie, Review


class MovieModelTest(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Test Movie",
            synopsis="Una sinopsis de prueba.",
            release_year=2020,
            genre="Drama",
            director="Test Director",
            duration=120,
        )

    def test_str_returns_title(self):
        self.assertEqual(str(self.movie), "Test Movie")

    def test_poster_accepts_blank(self):
        self.assertEqual(self.movie.poster, "")

    def test_average_rating_without_reviews_is_zero(self):
        self.assertEqual(self.movie.average_rating, 0)

    def test_average_rating_with_reviews(self):
        Review.objects.create(movie=self.movie, reviewer_name="Ana", rating=8, comment="Buena")
        Review.objects.create(movie=self.movie, reviewer_name="Luis", rating=6, comment="Regular")
        self.assertEqual(self.movie.average_rating, 7)


class HomeViewTest(TestCase):
    def setUp(self):
        Movie.objects.create(
            title="Home Movie", synopsis="...", release_year=2021,
            genre="Acción", director="X", duration=100,
        )

    def test_home_status_and_template(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movie/home.html")
        self.assertIn("movies", response.context)


class StatisticsViewTest(TestCase):
    def setUp(self):
        Movie.objects.create(
            title="Stat Movie", synopsis="...", release_year=2019,
            genre="Comedia, Drama", director="X", duration=90,
        )

    def test_statistics_status_and_graphics_present(self):
        response = self.client.get(reverse("statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("graphic", response.context)
        self.assertIn("graphic_genre", response.context)
        self.assertTrue(len(response.context["graphic"]) > 0)
        self.assertTrue(len(response.context["graphic_genre"]) > 0)


class SignupViewTest(TestCase):
    def test_signup_shows_email_in_context(self):
        response = self.client.get(reverse("signup"), {"email": "test@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["email"], "test@example.com")
        self.assertContains(response, "test@example.com")


class AddMoviesDbCommandTest(TestCase):
    def test_command_creates_movies_from_csv(self):
        self.assertEqual(Movie.objects.count(), 0)
        call_command("add_movies_db")
        self.assertGreater(Movie.objects.count(), 0)
```

**`news/tests.py`**
```python
import datetime

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import News


class NewsModelTest(TestCase):
    def test_str_returns_headline(self):
        n = News.objects.create(
            headline="Titular de prueba", body="Cuerpo", date=datetime.date(2024, 1, 1)
        )
        self.assertEqual(str(n), "Titular de prueba")

    def test_ordered_by_date_descending_in_view(self):
        News.objects.create(headline="Vieja", body="...", date=datetime.date(2020, 1, 1))
        News.objects.create(headline="Nueva", body="...", date=datetime.date(2024, 1, 1))
        response = self.client.get(reverse("news"))
        headlines = [n.headline for n in response.context["newss"]]
        self.assertEqual(headlines, ["Nueva", "Vieja"])


class NewsViewTest(TestCase):
    def test_news_status_ok(self):
        response = self.client.get(reverse("news"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news.html")


class AddNewsDbCommandTest(TestCase):
    def test_command_creates_five_news_with_parsed_dates(self):
        self.assertEqual(News.objects.count(), 0)
        call_command("add_news_db")
        self.assertEqual(News.objects.count(), 5)
        self.assertTrue(all(isinstance(n.date, datetime.date) for n in News.objects.all()))
```

### Cómo correrlos

```powershell
python manage.py test                              # todo el proyecto
python manage.py test movie                         # solo la app movie
python manage.py test news                          # solo la app news
python manage.py test movie.tests.MovieModelTest     # una clase específica
python manage.py test news.tests.NewsModelTest.test_str_returns_headline  # un test específico
```

Django crea una base de datos de prueba aparte (no toca `db.sqlite3`), corre los tests y la destruye al final — es seguro correrlos en cualquier momento.
