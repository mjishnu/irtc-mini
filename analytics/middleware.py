import logging
import threading
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SearchAnalyticsMiddleware:
    """
    Logs GET /api/trains/search/ requests to MongoDB via pymongo.
    """

    TARGET_PATH = "/api/trains/search/"

    def __init__(self, get_response):
        self.get_response = get_response
        self._collection = None

    # ── Lazy-init pymongo collection (one MongoClient per process) ──

    @property
    def collection(self):
        if self._collection is None:
            from pymongo import MongoClient
            from django.conf import settings

            client = MongoClient(settings.MONGO_URI)
            db = client[settings.DATABASES["mongo"]["NAME"]]
            self._collection = db["search_logs"]
        return self._collection

    # ── Middleware entry point ──────────────────────────────────────

    def __call__(self, request):
        # Fast exit for non-target requests
        if request.method != "GET" or request.path != self.TARGET_PATH:
            return self.get_response(request)

        start = time.monotonic()
        response = self.get_response(request)
        elapsed_ms = round((time.monotonic() - start) * 1000, 2)

        # Build the log document
        doc = {
            "endpoint": self.TARGET_PATH,
            "source": request.GET.get("source", ""),
            "destination": request.GET.get("destination", ""),
            "date": request.GET.get("date", ""),
            "user_id": (
                request.user.pk
                if hasattr(request, "user") and request.user.is_authenticated
                else None
            ),
            "execution_time_ms": elapsed_ms,
            "timestamp": datetime.now(timezone.utc),
        }

        # Fire-and-forget: write to MongoDB in a daemon thread
        threading.Thread(
            target=self._safe_insert,
            args=(doc,),
            daemon=True,
        ).start()

        return response

    # ── Threaded insert with error swallowing ──────────────────────

    def _safe_insert(self, doc: dict) -> None:
        """Insert a document into MongoDB; never let logging failures propagate."""
        try:
            self.collection.insert_one(doc)
        except Exception:
            logger.exception("Failed to log search request to MongoDB")
