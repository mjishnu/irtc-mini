from rest_framework import serializers

from .models import Train


class TrainSerializer(serializers.ModelSerializer):
    """
    Serializer for the Train model.
    Validates that available_seats ≤ total_seats and departure < arrival.
    """

    class Meta:
        model = Train
        fields = [
            "id",
            "train_number",
            "name",
            "source",
            "destination",
            "departure_time",
            "arrival_time",
            "total_seats",
            "available_seats",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        # On partial updates, fall back to the existing instance values
        total = attrs.get(
            "total_seats",
            getattr(self.instance, "total_seats", None),
        )
        available = attrs.get(
            "available_seats",
            getattr(self.instance, "available_seats", None),
        )
        if total is not None and available is not None and available > total:
            raise serializers.ValidationError(
                {"available_seats": ("Available seats cannot exceed total seats.")}
            )

        departure = attrs.get(
            "departure_time",
            getattr(self.instance, "departure_time", None),
        )
        arrival = attrs.get(
            "arrival_time",
            getattr(self.instance, "arrival_time", None),
        )
        if departure and arrival and departure >= arrival:
            raise serializers.ValidationError(
                {"departure_time": ("Departure time must be before arrival time.")}
            )

        return attrs
