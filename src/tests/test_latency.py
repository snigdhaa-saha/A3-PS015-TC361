# Import unittest, Python's built-in testing framework.
import unittest

# Import patch to simulate system commands without making real network calls.
from unittest.mock import patch, Mock

# Import the function we want to test.
from measurements.latency import measure_latency


class TestLatency(unittest.TestCase):
    """Tests for the latency measurement module."""

    def test_invalid_count_raises_error(self):
        # A ping count below 1 should not be accepted.
        with self.assertRaises(ValueError):
            measure_latency(count=0)

    @patch("measurements.latency.subprocess.run")
    def test_successful_ping(self, mock_run):
        # Simulate typical Linux ping output with two successful replies.
        mock_run.return_value = Mock(
            stdout=(
                "64 bytes from 8.8.8.8: time=20.0 ms\n"
                "64 bytes from 8.8.8.8: time=30.0 ms\n"
                "2 packets transmitted, 2 received, 0% packet loss\n"
            ),
            stderr="",
            returncode=0,
        )

        # Call the function without executing a real ping command.
        result = measure_latency(host="8.8.8.8", count=2)

        # Verify the key calculated results.
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["packets_sent"], 2)
        self.assertEqual(result["packets_received"], 2)
        self.assertEqual(result["packet_loss_percent"], 0.0)
        self.assertEqual(result["min_latency_ms"], 20.0)
        self.assertEqual(result["avg_latency_ms"], 25.0)
        self.assertEqual(result["max_latency_ms"], 30.0)

    @patch("measurements.latency.subprocess.run")
    def test_unrecognized_ping_output_returns_error(self, mock_run):
        mock_run.return_value = Mock(
            stdout="Unexpected ping output format",
            stderr="",
            returncode=1,
        )

        result = measure_latency(host="8.8.8.8", count=2)

        self.assertEqual(result["status"], "error")
        self.assertEqual(
            result["error"],
            "Could not parse ping packet summary",
        )

if __name__ == "__main__":
    # Run the tests when this file is executed directly.
    unittest.main()
