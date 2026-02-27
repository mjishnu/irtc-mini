from django.urls import path

from .views import CreateBookingView, MyBookingsView

urlpatterns = [
    path("", CreateBookingView.as_view(), name="booking-create"),
    path("my/", MyBookingsView.as_view(), name="booking-my"),
]
