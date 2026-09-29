from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("movies/", views.movie_list, name="movie_list"),
    path("movies/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("movies/<int:pk>/react/", views.react_to_movie, name="react_to_movie"),
    path("movies/<int:pk>/review/", views.add_review, name="add_review"),
    path("series/", views.series_list, name="series_list"),
    path("search/", views.search, name="search"),
]
