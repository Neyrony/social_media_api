import time
from typing import Any

from django.core.management.base import BaseCommand
from django.db import connection, OperationalError
from psycopg2 import OperationalError as PsycopgOperationalError


class Command(BaseCommand):
    help = "Wait for the database to be fully initialized."

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Checking database...")

        while True:
            try:
                connection.ensure_connection()
                self.stdout.write("Database connection established.")
                return
            except (OperationalError, PsycopgOperationalError):
                self.stdout.write("Waiting for database...")
                time.sleep(1)
