import logging

from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from pymongo import MongoClient
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class TopRouteSerializer(serializers.Serializer):
    """Serializer strictly for Swagger documentation of the top-routes response."""

    source = serializers.CharField()
    destination = serializers.CharField()
    search_count = serializers.IntegerField()


# ── Lazy pymongo collection accessor ─────────────────────────────

_client = None


def _get_collection():
    """Return the ``search_logs`` collection, reusing a single MongoClient."""
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)
    db = _client[settings.DATABASES["mongo"]["NAME"]]
    return db["search_logs"]


class TopRoutesView(APIView):
    """
    GET /api/analytics/top-routes/

    Returns the top 5 most-searched (source, destination) pairs
    using a MongoDB aggregation pipeline on the ``search_logs`` collection.

    Response format:
        [
            {"source": "Delhi", "destination": "Mumbai", "search_count": 42},
            ...
        ]
    """

    permission_classes = [AllowAny]
    authentication_classes = []  # public endpoint — skip JWT parsing

    @extend_schema(
        tags=["Analytics"],
        summary="Top searched routes",
        description=(
            "Returns the top 5 most-searched (source, destination) pairs "
            "using a MongoDB aggregation pipeline on the search_logs collection."
        ),
        responses={
            200: TopRouteSerializer(many=True),
            503: inline_serializer(
                name="ServiceUnavailable",
                fields={"error": serializers.CharField()},
            ),
        },
    )
    def get(self, request):
        collection = _get_collection()

        pipeline = [
            # Only consider logs that have both source and destination
            {
                "$match": {
                    "source": {"$ne": ""},
                    "destination": {"$ne": ""},
                }
            },
            # Group by (source, destination) pair and count
            {
                "$group": {
                    "_id": {
                        "source": "$source",
                        "destination": "$destination",
                    },
                    "count": {"$sum": 1},
                }
            },
            # Sort by count descending
            {"$sort": {"count": -1}},
            # Limit to top 5
            {"$limit": 5},
            # Reshape the output
            {
                "$project": {
                    "_id": 0,
                    "source": "$_id.source",
                    "destination": "$_id.destination",
                    "search_count": "$count",
                }
            },
        ]

        try:
            results = list(collection.aggregate(pipeline))
        except Exception:
            logger.exception("MongoDB aggregation failed for top-routes")
            return Response(
                {"error": "Analytics service is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(results)
