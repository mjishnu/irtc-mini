from django.contrib import admin

from .models import APILog


@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    """Admin configuration for API logs (read-only view)."""

    list_display = (
        "method",
        "path",
        "status_code",
        "user_id",
        "ip_address",
        "response_time_ms",
        "timestamp",
    )
    list_filter = ("method", "status_code")
    search_fields = ("path", "ip_address")
    list_per_page = 50
    readonly_fields = (
        "method",
        "path",
        "status_code",
        "user_id",
        "ip_address",
        "query_params",
        "request_body",
        "response_time_ms",
        "user_agent",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
