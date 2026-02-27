from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # ── OpenAPI schema & itneractive docs ──────────────────────────
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # ── App endpoints ──────────────────────────────────────────────
    path("api/", include("accounts.urls")),
    path("api/trains/", include("trains.urls")),
    path("api/bookings/", include("bookings.urls")),
    path("api/analytics/", include("analytics.urls")),
]
