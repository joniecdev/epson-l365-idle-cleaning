import unittest
import os
from unittest.mock import patch

os.environ.setdefault("PRINTER_HOST", "localhost")

from src.epson_l365.printer import Printer

class TestPrinter(unittest.TestCase):

    def setUp(self):
        self.printer = Printer()

    def test_initialization(self):
        self.assertIsNotNone(self.printer)

    def test_check_status(self):
        status = self.printer.check_status()
        self.assertIn(status, ['online', 'offline', 'error'])

    def test_send_print_job(self):
        result = self.printer.send_print_job("test_document.pdf")
        self.assertTrue(result)

    def test_perform_maintenance(self):
        with patch("src.epson_l365.printer.trigger_cleaning", return_value=True):
            result = self.printer.perform_maintenance()
        self.assertTrue(result)

    def test_handle_edge_cases(self):
        with self.assertRaises(ValueError):
            self.printer.send_print_job("")  # Test sending an empty job

if __name__ == '__main__':
    unittest.main()