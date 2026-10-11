
import unittest
from unittest.mock import patch, MagicMock
from measurements.connectivity import measure_connectivity


class TestConnectivity(unittest.TestCase):

    @patch("measurements.connectivity.socket.create_connection")
    def test_successful_connection(self, mock_connection):
        mock_connection.return_value = MagicMock()

        result = measure_connectivity(host="example.com", port=443)

        self.assertTrue(result["reachable"])
        self.assertEqual(result["status"], "success")
        self.assertIsNotNone(result["connection_time_ms"])
        mock_connection.assert_called_once()


if __name__ == "__main__":
    unittest.main()
