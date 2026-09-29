from django.contrib import admin

from .models import Movie, Reaction, Review


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("movie", "reviewer_name", "rating")


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("movie", "reaction_type", "created_at")
