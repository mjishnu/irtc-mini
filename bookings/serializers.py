from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from trains.models import Train
from trains.serializers import TrainSerializer

from .models import Booking


class CreateBookingSerializer(serializers.ModelSerializer):
    """
    Accepts a train PK and seat count.
    """

    train = serializers.PrimaryKeyRelatedField(queryset=Train.objects.all())

    class Meta:
        model = Booking
        fields = ["id", "pnr", "train", "seats_booked", "status", "booking_time"]
        read_only_fields = ["id", "pnr", "status", "booking_time"]

    def create(self, validated_data):
        train = validated_data["train"]
        seats_requested = validated_data["seats_booked"]
        user = validated_data["user"]

        with transaction.atomic():
            locked_train = Train.objects.select_for_update().get(pk=train.pk)

            if locked_train.departure_time <= timezone.now():
                raise serializers.ValidationError(
                    {"train": "Cannot book a train that has already departed."}
                )

            if locked_train.available_seats < seats_requested:
                raise serializers.ValidationError(
                    {
                        "seats_booked": (
                            f"Only {locked_train.available_seats} seat(s) "
                            f"available, but {seats_requested} requested."
                        )
                    }
                )

            locked_train.available_seats -= seats_requested
            locked_train.save(update_fields=["available_seats"])

            booking = Booking.objects.create(
                user=user,
                train=locked_train,
                seats_booked=seats_requested,
            )

        return booking


class BookingDetailSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for listing a user's bookings.
    Nests full train details via ``TrainSerializer``.
    """

    train = TrainSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "pnr",
            "train",
            "seats_booked",
            "status",
            "booking_time",
        ]
        read_only_fields = fields
