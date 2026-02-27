from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Booking
from .serializers import BookingDetailSerializer, CreateBookingSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Bookings"],
        summary="Book train seats",
        description=(
            "Book seats on a train. Requires JWT authentication.\n"
            "Uses `select_for_update()` internally to prevent race conditions."
        ),
    )
)
class CreateBookingView(CreateAPIView):
    """
    POST /api/bookings/

    Book seats on a train.  Requires JWT authentication.
    """

    serializer_class = CreateBookingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    get=extend_schema(
        tags=["Bookings"],
        summary="My Bookings",
        description="Returns the authenticated user's bookings (newest first) with nested train details.",
    )
)
class MyBookingsView(ListAPIView):
    """
    GET /api/bookings/my/

    Returns the authenticated user's bookings (newest first)
    with nested train details.
    """

    serializer_class = BookingDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            # drf-spectacular schema generation mock request
            return Booking.objects.none()

        return (
            Booking.objects.filter(user=self.request.user)
            .select_related("train")
            .order_by("-booking_time")
        )
