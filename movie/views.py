import base64
import io
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Movie, Reaction, Review


def _reaction_stats(movie):
    reactions = movie.reactions.all()
    total = reactions.count()
    positive = reactions.filter(reaction_type__in=["like", "love"]).count()
    positive_pct = round(positive / total * 100) if total else 0
    if positive_pct > 70:
        level = "positive"
    elif positive_pct >= 30:
        level = "neutral"
    else:
        level = "negative"
    return {"total": total, "positive_pct": positive_pct, "level": level}


def _genre_rows(queryset, all_genres, selected_genre):
    genres_to_use = [selected_genre] if selected_genre else all_genres
    rows = [(g, queryset.filter(genre=g).order_by("title")) for g in genres_to_use]
    return [(g, qs) for g, qs in rows if qs.exists()]


def home(request):
    all_titles = Movie.objects.all()
    top_rated = sorted(all_titles, key=lambda m: m.average_rating, reverse=True)[:6]
    genres = all_titles.values_list("genre", flat=True).distinct().order_by("genre")
    genre_rows = _genre_rows(all_titles, genres, None)
    return render(request, "movie/home.html", {
        "student_name": "Miguel Colorado",
        "featured_movies": top_rated,
        "hero_movies": top_rated[:4],
        "genre_rows": genre_rows,
        "movies": all_titles.order_by("title"),
    })


def about(request):
    return render(request, "movie/about.html")


def movie_list(request):
    genre = request.GET.get("genero", "").strip()
    genres = Movie.objects.values_list("genre", flat=True).distinct().order_by("genre")
    movies = Movie.objects.filter(content_type="movie")
    rows = _genre_rows(movies, genres, genre)
    return render(request, "movie/movie_list.html", {
        "rows": rows,
        "genres": genres,
        "selected_genre": genre,
        "section_title": "Películas",
    })


def series_list(request):
    genre = request.GET.get("genero", "").strip()
    genres = Movie.objects.values_list("genre", flat=True).distinct().order_by("genre")
    series = Movie.objects.filter(content_type="series")
    rows = _genre_rows(series, genres, genre)
    return render(request, "movie/series_list.html", {
        "rows": rows,
        "genres": genres,
        "selected_genre": genre,
        "section_title": "Series",
    })


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.reviews.order_by("-created_at")
    reacted_movies = request.session.get("reacted_movies", {})
    return render(request, "movie/movie_detail.html", {
        "movie": movie,
        "reviews": reviews,
        "reviews_count": reviews.count(),
        "stats": _reaction_stats(movie),
        "user_reaction": (reacted_movies.get(str(pk)) or {}).get("type"),
    })


@require_POST
def react_to_movie(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    reaction_type = request.POST.get("reaction_type")
    if reaction_type not in dict(Reaction.REACTION_CHOICES):
        return JsonResponse({"error": "Tipo de reacción inválido."}, status=400)

    reacted_movies = request.session.get("reacted_movies", {})
    existing = reacted_movies.get(str(pk))
    reaction = existing and Reaction.objects.filter(pk=existing["id"], movie=movie).first()

    if reaction:
        reaction.reaction_type = reaction_type
        reaction.save(update_fields=["reaction_type"])
    else:
        reaction = Reaction.objects.create(movie=movie, reaction_type=reaction_type)

    reacted_movies[str(pk)] = {"id": reaction.id, "type": reaction_type}
    request.session["reacted_movies"] = reacted_movies

    stats = _reaction_stats(movie)
    stats["user_reaction"] = reaction_type
    return JsonResponse(stats)


@login_required
@require_POST
def add_review(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    Review.objects.create(
        movie=movie,
        reviewer_name=request.user.first_name or request.user.username,
        rating=request.POST.get("rating"),
        comment=request.POST.get("comment", ""),
    )
    return redirect("movie_detail", pk=pk)


def _chart_to_base64(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def statistics_view(request):
    movies = Movie.objects.all()

    year_counts = Counter(m.release_year for m in movies if m.release_year)
    years = sorted(year_counts)
    fig1, ax1 = plt.subplots()
    ax1.bar(years, [year_counts[y] for y in years], color="#d97f3d")
    ax1.set_xlabel("Año")
    ax1.set_ylabel("Cantidad de películas")
    ax1.set_title("Películas por año")
    graphic = _chart_to_base64(fig1)

    genre_counts = Counter(
        m.genre.split(",")[0].strip() for m in movies if m.genre
    )
    genres = sorted(genre_counts, key=lambda g: genre_counts[g], reverse=True)
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.bar(genres, [genre_counts[g] for g in genres], color="#142521")
    ax2.set_xlabel("Género")
    ax2.set_ylabel("Cantidad de películas")
    ax2.set_title("Películas por género")
    plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
    graphic_genre = _chart_to_base64(fig2)

    return render(request, "statistics.html", {
        "graphic": graphic,
        "graphic_genre": graphic_genre,
    })


def signup(request):
    email = request.GET.get("email")
    return render(request, "signup.html", {"email": email})


def search(request):
    q = request.GET.get("q", "").strip()
    results = Movie.objects.filter(title__icontains=q) if q else Movie.objects.none()

    if request.GET.get("format") == "json":
        data = [{
            "id": m.pk,
            "title": m.title,
            "year": m.release_year,
            "poster": m.poster or "https://placehold.co/300x450?text=Sin+poster",
            "rating": round(m.average_rating, 1),
            "url": reverse("movie_detail", args=[m.pk]),
        } for m in results[:8]]
        return JsonResponse({"results": data})

    return render(request, "movie/search_results.html", {
        "query": q,
        "results": results,
    })
