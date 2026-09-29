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
