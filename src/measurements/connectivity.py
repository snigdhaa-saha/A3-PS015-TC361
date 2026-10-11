# Import socket to establish a TCP connection.
import socket

# Import time to measure how long the connection takes.
import time


def measure_connectivity(host="example.com", port=443, timeout=5):
    """
    Test whether a TCP connection can be established.

    Parameters:
        host: The destination hostname or IP address.
        port: The destination TCP port (443 is commonly used for HTTPS).
        timeout: Maximum time to wait for the connection, in seconds.

    Returns:
        A dictionary containing the connectivity test results.
    """

    # Record the start time before attempting the connection.
    start_time = time.perf_counter()

    # Set up the default result values.
    result = {
        "host": host,
        "port": port,
        "reachable": False,
        "connection_time_ms": None,
        "status": "error",
        "error": None,
    }

    try:
        # Attempt a TCP connection.
        # The context manager automatically closes the socket afterward.
        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ):
            # Calculate elapsed connection time in milliseconds.
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Save the successful connection results.
            result["reachable"] = True
            result["connection_time_ms"] = round(elapsed_ms, 2)
            result["status"] = "success"

    # Handle connection timeouts.
    except socket.timeout:
        result["status"] = "failed"
        result["error"] = "Connection timed out"
        result["connection_time_ms"] = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

    # Handle DNS lookup and other socket connection errors.
    except OSError as exc:
        result["status"] = "failed"
        result["error"] = str(exc)
        result["connection_time_ms"] = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

    # Return the complete result dictionary.
    return result
