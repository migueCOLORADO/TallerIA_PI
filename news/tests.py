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
