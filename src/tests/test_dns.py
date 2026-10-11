# Import unittest for writing automated tests.
import unittest

# Import patch to simulate DNS lookup results without using the network.
from unittest.mock import patch

# Import the DNS measurement function.
from measurements.dns import measure_dns


class TestDNS(unittest.TestCase):
    """Tests for the DNS measurement module."""

    @patch("measurements.dns.socket.getaddrinfo")
    def test_successful_dns_resolution(self, mock_getaddrinfo):
        # Simulate a successful lookup returning an IPv4 address.
        mock_getaddrinfo.return_value = [
            (2, 1, 6, "", ("93.184.216.34", 0))
        ]

        # Run the DNS measurement.
        result = measure_dns("example.com")

        # Verify the hostname was resolved successfully.
        self.assertTrue(result["resolved"])
        self.assertEqual(result["status"], "success")
        self.assertIn("93.184.216.34", result["ip_addresses"])
        self.assertIsNotNone(result["dns_lookup_ms"])
        self.assertIsNone(result["error"])

    @patch("measurements.dns.socket.getaddrinfo")
    def test_failed_dns_resolution(self, mock_getaddrinfo):
        # Simulate a hostname that cannot be resolved.
        mock_getaddrinfo.side_effect = OSError(
            "Name or service not known"
        )

        # Run the DNS measurement.
        result = measure_dns("invalid.example")

        # Verify the failure is reported instead of crashing.
        self.assertFalse(result["resolved"])
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["ip_addresses"], [])
        self.assertIsNotNone(result["error"])


if __name__ == "__main__":
    # Execute the tests when this file is run directly.
    unittest.main()
