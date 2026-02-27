from django.contrib import admin

from .models import Train


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    """Admin configuration for Train model."""

    list_display = (
        "train_number",
        "name",
        "source",
        "destination",
        "departure_time",
        "arrival_time",
        "total_seats",
        "available_seats",
    )
    list_filter = ("source", "destination", "departure_time")
    search_fields = ("train_number", "name", "source", "destination")
    list_per_page = 25
    readonly_fields = ("id",)
