from datetime import datetime, time

import django_filters
from django.utils import timezone

from .models import Train


class TrainFilter(django_filters.FilterSet):
    """
    Filters for GET /api/trains/search/

    Query params:
        source       — partial, case-insensitive match on departure station
        destination  — partial, case-insensitive match on arrival station
        date         — YYYY-MM-DD; returns trains departing on that calendar day
    """

    source = django_filters.CharFilter(
        field_name="source",
        lookup_expr="icontains",
        help_text="Partial match on departure station name",
    )
    destination = django_filters.CharFilter(
        field_name="destination",
        lookup_expr="icontains",
        help_text="Partial match on arrival station name",
    )
    date = django_filters.DateFilter(
        method="filter_by_date",
        help_text="Filter trains departing on this date (YYYY-MM-DD)",
    )

    class Meta:
        model = Train
        fields = ["source", "destination", "date"]

    def filter_by_date(self, queryset, name, value):
        """
        Filter trains whose ``departure_time`` falls within *value* day
        (midnight-to-midnight), timezone-aware.
        """
        if value is None:
            return queryset

        day_start = timezone.make_aware(
            datetime.combine(value, time.min),
            timezone.get_current_timezone(),
        )
        day_end = timezone.make_aware(
            datetime.combine(value, time.max),
            timezone.get_current_timezone(),
        )
        return queryset.filter(departure_time__range=(day_start, day_end))
