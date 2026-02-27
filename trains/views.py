from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.permissions import IsAdminUserRole

from drf_spectacular.utils import extend_schema, extend_schema_view

from .filters import TrainFilter
from .models import Train
from .serializers import TrainSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Trains"],
        summary="Create a new train",
        description="Create a new train. Restricted to admin-role users only.",
    )
)
class TrainListCreateView(CreateAPIView):
    """
    POST /api/trains/

    Create a new train. Restricted to admin-role users only.
    """

    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserRole]


@extend_schema_view(
    get=extend_schema(
        tags=["Trains"],
        summary="Retrieve a train",
        description="Retrieve a train's details (admin only).",
    ),
    put=extend_schema(
        tags=["Trains"],
        summary="Update a train",
        description="Full update (admin only).",
    ),
    patch=extend_schema(
        tags=["Trains"],
        summary="Partial update a train",
        description="Partial update (admin only).",
    ),
)
class TrainDetailView(RetrieveUpdateAPIView):
    """
    GET    /api/trains/<pk>/   — Retrieve a train's details (admin only).
    PUT    /api/trains/<pk>/   — Full update (admin only).
    PATCH  /api/trains/<pk>/   — Partial update (admin only).
    """

    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserRole]


@extend_schema_view(
    get=extend_schema(
        tags=["Trains"],
        summary="Search trains",
        description=(
            "Public endpoint — search trains by source, destination, and/or date.\n"
            "Supports LimitOffset pagination via `?limit=N&offset=M`.\n\n"
            "Filters (all optional):\n"
            "• `source` — partial match on departure station\n"
            "• `destination` — partial match on arrival station\n"
            "• `date` — YYYY-MM-DD; trains departing on that calendar day"
        ),
    )
)
class TrainSearchView(ListAPIView):
    """
    GET /api/trains/search/?source=Delhi&destination=Mumbai&date=2026-03-01

    Public endpoint — search trains by source, destination, and/or date.
    Supports LimitOffset pagination via ``?limit=N&offset=M``.

    Filters (all optional):
        source       — partial, case-insensitive match on departure station
        destination  — partial, case-insensitive match on arrival station
        date         — YYYY-MM-DD; trains departing on that calendar day
    """

    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    filterset_class = TrainFilter
    pagination_class = LimitOffsetPagination
