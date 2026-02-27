from django.db import models

from django_mongodb_backend.fields import ObjectIdAutoField


class APILog(models.Model):
    """
    Stores API request/response metadata in MongoDB.
    Uses ObjectIdAutoField for native MongoDB _id support.
    No foreign keys to MySQL models — uses plain integer user_id
    to avoid cross-database joins.
    """

    id = ObjectIdAutoField(primary_key=True)

    method = models.CharField(
        max_length=10,
        help_text="HTTP method (GET, POST, PUT, DELETE, etc.)",
    )
    path = models.CharField(
        max_length=500,
        help_text="Request URL path",
    )
    status_code = models.IntegerField(
        help_text="HTTP response status code",
    )
    user_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID of the authenticated user (if any)",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Client IP address",
    )
    query_params = models.JSONField(
        default=dict,
        blank=True,
        help_text="URL query parameters",
    )
    request_body = models.JSONField(
        default=dict,
        blank=True,
        help_text="Request body payload (sanitised)",
    )
    response_time_ms = models.FloatField(
        default=0,
        help_text="Response time in milliseconds",
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Client User-Agent string",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the request was logged",
    )

    class Meta:
        db_table = "api_logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.method}] {self.path} → {self.status_code} ({self.response_time_ms:.0f}ms)"
