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


# ---------------------------------------------------------------------------
# Taller 3 — IA: embeddings, carga desde CSV/carpeta y sistema de recomendación
# ---------------------------------------------------------------------------
import csv
import shutil
import tempfile
from io import StringIO
from pathlib import Path

import numpy as np
from django.test import override_settings

from .ai_utils import (
    bytes_to_embedding,
    cosine_similarity,
    embedding_to_bytes,
    get_embeddings,
    movie_document,
)
from .poster_utils import poster_filename


def _make_movie(title, synopsis="Sinopsis de prueba.", genre="Drama", **kwargs):
    return Movie.objects.create(
        title=title, synopsis=synopsis, release_year=2000, genre=genre,
        director="Test", duration=100, **kwargs,
    )


class EmbeddingFieldTest(TestCase):
    def test_emb_accepts_binary_and_reads_back_with_frombuffer(self):
        vector = np.array([0.1, -0.2, 0.3, 0.4], dtype=np.float32)
        movie = _make_movie("Emb Movie", emb=vector.tobytes())

        movie.refresh_from_db()
        restored = np.frombuffer(movie.emb, dtype=np.float32)
        np.testing.assert_array_equal(restored, vector)
        np.testing.assert_array_equal(bytes_to_embedding(movie.emb), vector)

    def test_emb_is_optional(self):
        self.assertIsNone(_make_movie("No Emb").emb)


class CosineSimilarityTest(TestCase):
    def test_identical_vectors_is_one(self):
        v = np.array([1.0, 2.0, 3.0])
        self.assertAlmostEqual(cosine_similarity(v, v), 1.0, places=6)

    def test_orthogonal_vectors_is_zero(self):
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0, places=6)

    def test_opposite_vectors_is_minus_one(self):
        self.assertAlmostEqual(cosine_similarity([1.0, 1.0], [-1.0, -1.0]), -1.0, places=6)

    def test_zero_vector_does_not_divide_by_zero(self):
        self.assertEqual(cosine_similarity([0.0, 0.0], [1.0, 0.0]), 0.0)


class UpdateMoviesFromCsvCommandTest(TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmpdir)

    def test_updates_synopsis_and_reports_missing_titles(self):
        movie = _make_movie("Csv Movie", synopsis="Original")
        csv_path = self.tmpdir / "descriptions.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Title", "Updated Description"])
            writer.writeheader()
            writer.writerow({"Title": "Csv Movie", "Updated Description": "Sinopsis enriquecida."})
            writer.writerow({"Title": "No Existe", "Updated Description": "X"})

        out = StringIO()
        call_command("update_movies_from_csv", csv=str(csv_path), stdout=out)

        movie.refresh_from_db()
        self.assertEqual(movie.synopsis, "Sinopsis enriquecida.")
        self.assertIn("Películas actualizadas: 1", out.getvalue())
        self.assertIn("No Existe", out.getvalue())


class UpdateImagesFromFolderCommandTest(TestCase):
    def setUp(self):
        self.media_root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.media_root)

    def test_assigns_poster_from_matching_file(self):
        with_file = _make_movie("Mad Max: Fury Road")
        without_file = _make_movie("Sin Poster", poster="https://example.com/original.jpg")

        images = self.media_root / "movie" / "images"
        images.mkdir(parents=True)
        (images / poster_filename(with_file.title)).write_bytes(b"png")
        (images / "m_huerfano.png").write_bytes(b"png")

        out = StringIO()
        with override_settings(MEDIA_ROOT=self.media_root, MEDIA_URL="/media/"):
            call_command("update_images_from_folder", stdout=out)

        with_file.refresh_from_db()
        without_file.refresh_from_db()
        self.assertEqual(with_file.poster, "/media/movie/images/m_mad-max-fury-road.png")
        self.assertEqual(without_file.poster, "https://example.com/original.jpg")
        self.assertIn("Pósters asignados: 1", out.getvalue())
        self.assertIn("m_huerfano.png", out.getvalue())


class RecommendViewTest(TestCase):
    """Usa el modelo local real de sentence-transformers (sin APIs externas)."""

    @classmethod
    def setUpTestData(cls):
        movies = [
            _make_movie("Viaje Estelar", genre="Ciencia Ficción",
                        synopsis="Astronautas viajan por el espacio a través de un agujero de gusano para salvar a la humanidad."),
            _make_movie("Risas en la Oficina", genre="Comedia",
                        synopsis="Un grupo de compañeros de trabajo vive situaciones absurdas y divertidas en la oficina."),
            _make_movie("La Familia", genre="Crimen",
                        synopsis="El jefe de una familia mafiosa entrega su imperio criminal a su hijo menor."),
        ]
        for movie, emb in zip(movies, get_embeddings(movie_document(m) for m in movies)):
            movie.emb = embedding_to_bytes(emb)
            movie.save(update_fields=["emb"])
        _make_movie("Sin Embedding")

    def test_get_returns_200_and_template(self):
        response = self.client.get(reverse("recommend"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movie/recommend.html")
        self.assertTemplateUsed(response, "movie/base.html")
        self.assertNotIn("movie", response.context)

    def test_post_with_valid_prompt_returns_a_movie(self):
        response = self.client.post(reverse("recommend"), {"prompt": "película sobre viajes espaciales y astronautas"})
        self.assertEqual(response.status_code, 200)
        movie = response.context["movie"]
        self.assertIsNotNone(movie)
        self.assertEqual(movie.title, "Viaje Estelar")
        self.assertGreaterEqual(response.context["similarity"], -1.0)
        self.assertLessEqual(response.context["similarity"], 1.0)
        self.assertNotIn("Sin Embedding", [m.title for m, _ in response.context["alternatives"]])
        self.assertContains(response, "Viaje Estelar")

    def test_post_with_empty_prompt_shows_error(self):
        response = self.client.post(reverse("recommend"), {"prompt": "   "})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("movie", response.context)
        self.assertIn("error", response.context)

    def test_post_without_embeddings_does_not_crash(self):
        Movie.objects.update(emb=None)
        response = self.client.post(reverse("recommend"), {"prompt": "una comedia"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("movie", response.context)
        self.assertContains(response, "Todavía no hay películas con embeddings")

    def test_navbar_has_recommend_link(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'href="/recommend/"')
