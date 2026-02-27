import uuid

from django.conf import settings
from django.db import IntegrityError
from django.core.validators import MinValueValidator
from django.db import models


class BookingStatus(models.TextChoices):
    """Possible states of a booking."""

    CONFIRMED = "CONFIRMED", "Confirmed"
    WAITLISTED = "WAITLISTED", "Waitlisted"
    CANCELLED = "CANCELLED", "Cancelled"


class Booking(models.Model):
    """
    Represents a ticket booking made by a user for a specific train.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="The passenger who made this booking",
    )
    train = models.ForeignKey(
        "trains.Train",
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="The train for which this booking was made",
    )
    seats_booked = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of seats reserved in this booking",
    )
    booking_time = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the booking was created",
    )
    status = models.CharField(
        max_length=12,
        choices=BookingStatus.choices,
        default=BookingStatus.CONFIRMED,
        help_text="Current status of the booking",
    )
    pnr = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        help_text="Auto-generated PNR number",
    )

    class Meta:
        db_table = "bookings"
        indexes = [
            models.Index(fields=["user", "booking_time"], name="idx_booking_user_time"),
            models.Index(fields=["pnr"], name="idx_booking_pnr"),
            models.Index(fields=["train", "status"], name="idx_booking_train_status"),
            models.Index(fields=["status"], name="idx_booking_status"),
        ]
        ordering = ["-booking_time"]

    _PNR_MAX_RETRIES = 10

    def save(self, *args, **kwargs):
        if not self.pnr:
            self.pnr = self._generate_pnr()

        # Retry loop to handle the (unlikely but possible) PNR collision
        for attempt in range(self._PNR_MAX_RETRIES):
            try:
                super().save(*args, **kwargs)
                return
            except IntegrityError as exc:
                if (
                    "pnr" not in str(exc).lower()
                    or attempt == self._PNR_MAX_RETRIES - 1
                ):
                    raise
                self.pnr = self._generate_pnr()
                self.pk = None  # force INSERT on retry

    @staticmethod
    def _generate_pnr():
        """Generate a 10-character uppercase PNR."""
        return uuid.uuid4().hex[:10].upper()

    def __str__(self):
        return (
            f"PNR {self.pnr} — {self.user.email} | "
            f"{self.train.train_number} | {self.seats_booked} seat(s) | {self.status}"
        )
