from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Movie(models.Model):
    CONTENT_TYPE_CHOICES = [
        ("movie", "Película"),
        ("series", "Serie"),
    ]

    title = models.CharField(max_length=200)
    synopsis = models.TextField()
    release_year = models.IntegerField()
    genre = models.CharField(max_length=100)
    poster = models.URLField(blank=True)
    director = models.CharField(max_length=200)
    duration = models.IntegerField(help_text="Duración en minutos")
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default="movie")

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)

    def __str__(self):
        return self.title


class Review(models.Model):
    movie = models.ForeignKey(Movie, related_name="reviews", on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=100)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movie.title} - {self.rating}"


class Reaction(models.Model):
    REACTION_CHOICES = [
        ("like", "Like"),
        ("love", "Love"),
        ("dislike", "Dislike"),
    ]

    movie = models.ForeignKey(Movie, related_name="reactions", on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movie.title} - {self.reaction_type}"
