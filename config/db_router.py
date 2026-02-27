MONGO_APPS = {"analytics"}


class DatabaseRouter:
    """Route analytics models to MongoDB; everything else to MySQL."""

    def db_for_read(self, model, **hints):
        if model._meta.app_label in MONGO_APPS:
            return "mongo"
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label in MONGO_APPS:
            return "mongo"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations only within the same database
        db1 = "mongo" if obj1._meta.app_label in MONGO_APPS else "default"
        db2 = "mongo" if obj2._meta.app_label in MONGO_APPS else "default"
        return db1 == db2

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in MONGO_APPS:
            return db == "mongo"
        return db == "default"
