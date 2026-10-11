# Import socket to perform DNS lookups using the operating system's
# configured name-resolution system.
import socket

# Import time to measure how long the lookup takes.
import time


def measure_dns(host="example.com"):
    """
    Measure the time required to resolve a hostname.

    Parameters:
        host: The domain name to resolve.

    Returns:
        A dictionary containing DNS resolution results.
    """

    # Record the starting time before performing the lookup.
    start_time = time.perf_counter()

    # Prepare a dictionary with default values.
    result = {
        "host": host,
        "resolved": False,
        "ip_addresses": [],
        "dns_lookup_ms": None,
        "status": "error",
        "error": None,
    }

    try:
        # Ask the operating system to resolve the hostname.
        # SOCK_STREAM requests addresses suitable for TCP connections.
        addresses = socket.getaddrinfo(
            host,
            None,
            type=socket.SOCK_STREAM,
        )

        # Calculate elapsed time in milliseconds.
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Extract unique IP addresses from the lookup results.
        # The address is stored at index 4 of each getaddrinfo result.
        ip_addresses = list(
            dict.fromkeys(item[4][0] for item in addresses)
        )

        # Store the successful lookup results.
        result["resolved"] = bool(ip_addresses)
        result["ip_addresses"] = ip_addresses
        result["dns_lookup_ms"] = round(elapsed_ms, 2)

        # Mark the lookup as successful only if addresses were returned.
        if ip_addresses:
            result["status"] = "success"
        else:
            result["status"] = "failed"
            result["error"] = "No IP addresses returned"

    # Handle cases where the hostname cannot be resolved.
    except OSError as exc:
        result["error"] = str(exc)
        result["status"] = "failed"

        # Record elapsed time even when resolution fails.
        result["dns_lookup_ms"] = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

    # Return the DNS measurement.
    return result
