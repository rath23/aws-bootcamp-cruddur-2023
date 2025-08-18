from lib.db import db

class AddBioColumnMigration:
    def migrate_sql(self):
        return """
            ALTER TABLE public.users ADD COLUMN bio text;
        """

    def rollback_sql(self):
        return """
            ALTER TABLE public.users DROP COLUMN bio;
        """

    def migrate(self):
        db.query_commit(self.migrate_sql(), {})

    def rollback(self):
        db.query_commit(self.rollback_sql(), {})

migration = AddBioColumnMigration()
