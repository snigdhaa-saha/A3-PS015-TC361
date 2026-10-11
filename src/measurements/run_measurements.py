# Import json to format the results as readable JSON.
import json

# Import datetime to record when the measurements were collected.
from datetime import datetime, timezone

# Import the three measurement functions from their modules.
from measurements.latency import measure_latency
from measurements.dns import measure_dns
from measurements.connectivity import measure_connectivity


def run_all_measurements(host="example.com"):
    """
    Run the latency, DNS, and TCP connectivity measurements.

    Returns:
        A dictionary containing a timestamp and all measurement results.
    """

    # Record the time when this measurement run begins.
    timestamp = datetime.now(timezone.utc).isoformat()

    # Run the latency test against the host's IP address.
    # This checks reachability and packet loss to 8.8.8.8 by default.
    latency_result = measure_latency()

    # Check whether the specified hostname resolves to IP addresses.
    dns_result = measure_dns(host)

    # Check whether a TCP connection can be established on port 443.
    connectivity_result = measure_connectivity(host, port=443)

    # Combine all results into a single structured dictionary.
    report = {
        "project": "NetSages",
        "timestamp_utc": timestamp,
        "target_host": host,
        "measurements": {
            "latency": latency_result,
            "dns": dns_result,
            "connectivity": connectivity_result,
        },
    }

    # Return the complete report.
    return report


if __name__ == "__main__":
    # Execute all measurements when this file is run directly.
    results = run_all_measurements()

    # Print the results as indented JSON for easy reading and saving.
    print(json.dumps(results, indent=4))
