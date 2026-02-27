"""
Seed the database with sample trains and generate MongoDB search logs.

Usage (inside Docker):
    python manage.py seed_data
    python manage.py seed_data --flush   # clear existing data first
"""

import random
import time
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.utils import timezone

SAMPLE_TRAINS = [
    {
        "train_number": "12301",
        "name": "Rajdhani Express",
        "source": "New Delhi",
        "destination": "Mumbai Central",
        "total_seats": 500,
    },
    {
        "train_number": "12302",
        "name": "Duronto Express",
        "source": "Mumbai Central",
        "destination": "New Delhi",
        "total_seats": 450,
    },
    {
        "train_number": "12657",
        "name": "Chennai Mail",
        "source": "Bangalore",
        "destination": "Chennai",
        "total_seats": 600,
    },
    {
        "train_number": "12839",
        "name": "Howrah Mail",
        "source": "Chennai",
        "destination": "Howrah",
        "total_seats": 550,
    },
    {
        "train_number": "12951",
        "name": "Mumbai Rajdhani",
        "source": "New Delhi",
        "destination": "Mumbai Central",
        "total_seats": 480,
    },
    {
        "train_number": "12259",
        "name": "Sealdah Duronto",
        "source": "Kolkata",
        "destination": "New Delhi",
        "total_seats": 400,
    },
]

SEARCH_QUERIES = [
    {"source": "New Delhi", "destination": "Mumbai Central"},
    {"source": "New Delhi", "destination": "Mumbai Central"},
    {"source": "New Delhi", "destination": "Mumbai Central"},
    {"source": "Bangalore", "destination": "Chennai"},
    {"source": "Bangalore", "destination": "Chennai"},
    {"source": "Kolkata", "destination": "New Delhi"},
    {"source": "Chennai", "destination": "Howrah"},
    {"source": "Mumbai Central", "destination": "New Delhi"},
    {"source": "New Delhi", "destination": "Mumbai Central", "date": "2026-03-15"},
    {"source": "", "destination": "", "date": "2026-03-20"},
]


class Command(BaseCommand):
    help = "Seed trains and generate MongoDB search logs for demonstration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing seed data before inserting.",
        )

    def handle(self, *args, **options):
        self._seed_trains(flush=options["flush"])
        self._generate_search_logs(flush=options["flush"])
        self.stdout.write(self.style.SUCCESS("\n✅ Seeding complete!"))

    # ── Trains ────────────────────────────────────────────────────

    def _seed_trains(self, flush=False):
        from trains.models import Train

        if flush:
            deleted, _ = Train.objects.filter(
                train_number__in=[t["train_number"] for t in SAMPLE_TRAINS]
            ).delete()
            self.stdout.write(f"  Flushed {deleted} existing train(s)")

        now = timezone.now()
        created = 0
        for i, data in enumerate(SAMPLE_TRAINS):
            _, was_created = Train.objects.get_or_create(
                train_number=data["train_number"],
                defaults={
                    "name": data["name"],
                    "source": data["source"],
                    "destination": data["destination"],
                    "departure_time": now + timedelta(days=i + 1, hours=6),
                    "arrival_time": now + timedelta(days=i + 1, hours=22),
                    "total_seats": data["total_seats"],
                    "available_seats": data["total_seats"],
                },
            )
            if was_created:
                created += 1

        self.stdout.write(
            f"  🚆  Trains: {created} created, {len(SAMPLE_TRAINS) - created} already existed"
        )

    # ── Search logs (MongoDB) ─────────────────────────────────────

    def _generate_search_logs(self, flush=False):
        from datetime import datetime, timezone as tz

        from pymongo import MongoClient

        client = MongoClient(settings.MONGO_URI)
        db = client[settings.DATABASES["mongo"]["NAME"]]
        collection = db["search_logs"]

        if flush:
            result = collection.delete_many({})
            self.stdout.write(
                f"  Flushed {result.deleted_count} existing search log(s)"
            )

        docs = []
        base_time = datetime.now(tz.utc)

        for i, query in enumerate(SEARCH_QUERIES):
            doc = {
                "endpoint": "/api/trains/search/",
                "source": query.get("source", ""),
                "destination": query.get("destination", ""),
                "date": query.get("date", ""),
                "user_id": random.choice([None, None, 1, 2]),
                "execution_time_ms": round(random.uniform(5.0, 30.0), 2),
                "timestamp": base_time - timedelta(minutes=random.randint(1, 120)),
            }
            docs.append(doc)

        collection.insert_many(docs)
        self.stdout.write(
            f"  📊  Search logs: {len(docs)} documents inserted into MongoDB"
        )
