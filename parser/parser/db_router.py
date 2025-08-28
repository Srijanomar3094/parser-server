class ContractsRouter:
    """Route models in the contracts app to the 'mongo' database.

    - contracts app -> 'mongo'
    - everything else -> default handling
    """

    app_label = "contracts"
    mongo_alias = "mongo"

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.mongo_alias
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.mongo_alias
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == self.app_label or obj2._meta.app_label == self.app_label:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Prevent Django migrations for contracts in SQL DBs; Djongo manages schema on mongo
        if app_label == self.app_label:
            return db == self.mongo_alias
        return None


