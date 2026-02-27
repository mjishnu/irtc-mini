from django.db import models


class Train(models.Model):
    """
    Represents a train with its route and seat information.
    """

    train_number = models.CharField(
        max_length=10,
        unique=True,
        help_text="Unique train number, e.g. 12301",
    )
    name = models.CharField(
        max_length=120,
        help_text="Train name, e.g. Rajdhani Express",
    )
    source = models.CharField(
        max_length=120,
        help_text="Departure station name",
    )
    destination = models.CharField(
        max_length=120,
        help_text="Arrival station name",
    )
    departure_time = models.DateTimeField(
        help_text="Scheduled departure date & time",
    )
    arrival_time = models.DateTimeField(
        help_text="Scheduled arrival date & time",
    )
    total_seats = models.PositiveIntegerField(
        help_text="Total number of seats on this train",
    )
    available_seats = models.PositiveIntegerField(
        help_text="Currently available seats for booking",
    )

    class Meta:
        db_table = "trains"
        indexes = [
            # Composite index — most common search: "trains from A to B"
            models.Index(
                fields=["source", "destination"],
                name="idx_train_src_dest",
            ),
            # Single-column indexes for filtered searches
            models.Index(fields=["train_number"], name="idx_train_number"),
            models.Index(fields=["source"], name="idx_train_source"),
            models.Index(fields=["destination"], name="idx_train_destination"),
            models.Index(fields=["departure_time"], name="idx_train_departure"),
        ]
        ordering = ["departure_time"]

    def __str__(self):
        return f"{self.train_number} — {self.name} ({self.source} → {self.destination})"

    @property
    def is_available(self):
        """Check if seats are still available for booking."""
        return self.available_seats > 0
