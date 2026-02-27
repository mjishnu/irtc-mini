from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for the Booking model."""

    list_display = (
        "pnr",
        "user",
        "train",
        "seats_booked",
        "status",
        "booking_time",
    )
    list_filter = ("status", "booking_time")
    search_fields = ("pnr", "user__email", "train__train_number")
    list_per_page = 25
    readonly_fields = ("pnr", "booking_time")
    raw_id_fields = ("user", "train")
