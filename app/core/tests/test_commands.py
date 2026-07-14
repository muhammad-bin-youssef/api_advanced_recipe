from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2OpError

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_checked):
        """Test waiting for database if database ready."""
        patched_checked.return_value = True

        call_command("wait_for_db")

        patched_checked.assertEqual(patched_checked.call_count, 1)

    @patch("time.sleep")
    def test_wait_for_db_delay(self, patched_sleep, patched_checked):
        """Test waiting for database when getting OperationalError."""
        patched_checked.side_effect = (
            [Psycopg2OpError] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        self.assertEqual(patched_checked.call_count, 6)
        patched_checked.assert_called_with(databases=["default"])
