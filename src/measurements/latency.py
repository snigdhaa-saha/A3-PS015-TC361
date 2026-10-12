# Import platform to identify the operating system (Windows, Linux, etc.).
import platform

# Import re to search for patterns in the ping command's output.
import re

# Import subprocess to execute the system's ping command from Python.
import subprocess


def measure_latency(host="8.8.8.8", count=4, timeout=10):
    """
    Measure network latency and packet loss using the ping command.

    Parameters:
        host: The destination IP address or domain name to ping.
        count: The number of ping requests to send.
        timeout: The maximum wait time for each request, in seconds
                 on Linux and milliseconds (after conversion) on Windows.

    Returns:
        A dictionary containing the measurement results.
    """

    # Reject invalid input: at least one ping request must be sent.
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise ValueError("count must be a positive integer")

    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("timeout must be a positive number")
    if not isinstance(host, str) or not host.strip():
        raise ValueError("host must be a non-empty string")

    # Identify the operating system so we can construct the correct command.
    system = platform.system().lower()

    # Windows uses -n to specify the number of requests and -w for timeout
    # in milliseconds.
    if system == "windows":
        command = [
            "ping",
            "-n", str(count),
            "-w", str(timeout * 1000),
            host
        ]

    # Linux and most Unix-like systems use -c for count and -W for timeout
    # in seconds.
    else:
        command = [
            "ping",
            "-c", str(count),
            "-W", str(timeout),
            host
        ]

    # Initialize the result dictionary with safe default values.
    # None means that a latency measurement is unavailable.
    result = {
        "host": host,
        "packets_sent": count,
        "packets_received": 0,
        "packet_loss_percent": 100.0,
        "min_latency_ms": None,
        "avg_latency_ms": None,
        "max_latency_ms": None,
        "status": "error",
        "error": None,
    }

    try:
        # Execute the ping command.
        # capture_output collects standard output and error output.
        # text=True returns output as strings instead of bytes.
        # check=False prevents an exception when ping exits with a
        # non-zero exit code, which can happen when packets are lost.
        # The overall timeout prevents the program from waiting forever.
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=(count * timeout) + 5,
            check=False,
        )

        # Combine both output streams because error messages may appear
        # in either one.
        output = completed.stdout + "\n" + completed.stderr

        # Look for the Linux-style summary, for example:
        # "4 packets transmitted, 3 received, 25% packet loss"
        #
        # The regular expression captures:
        # Group 1 = packets transmitted
        # Group 2 = packets received
        loss_match = re.search(
            r"(\d+)\s+packets transmitted,\s*(\d+)\s+"
            r"(?:packets )?received",
            output,
            re.IGNORECASE,
        )

        sent_match = None
        received_match = None

        if loss_match:
            result["packets_sent"] = int(loss_match.group(1))
            result["packets_received"] = int(loss_match.group(2))
        else:
            sent_match = re.search(
                r"Sent\s*=\s*(\d+)", output, re.IGNORECASE
            )
            received_match = re.search(
                r"Received\s*=\s*(\d+)", output, re.IGNORECASE
            )

            if sent_match and received_match:
                result["packets_sent"] = int(sent_match.group(1))
                result["packets_received"] = int(received_match.group(1))

        if not loss_match and not (sent_match and received_match):
            result["status"] = "error"
            result["error"] = "Could not parse ping packet summary"
            return result

        # If the Linux-style summary was found, save the packet counts.
        if loss_match:
            result["packets_sent"] = int(loss_match.group(1))
            result["packets_received"] = int(loss_match.group(2))

        else:
            # Windows uses a different summary format, for example:
            # "Packets: Sent = 4, Received = 3, Lost = 1 (25% loss)"
            sent_match = re.search(
                r"Sent\s*=\s*(\d+)", output, re.IGNORECASE
            )

            received_match = re.search(
                r"Received\s*=\s*(\d+)", output, re.IGNORECASE
            )

            # Update the counts only when both values were found.
            if sent_match and received_match:
                result["packets_sent"] = int(sent_match.group(1))
                result["packets_received"] = int(received_match.group(1))

        # Retrieve the final packet counts.
        sent = result["packets_sent"]
        received = result["packets_received"]

        # Calculate packet loss as a percentage.
        # Example: 1 lost packet out of 4 means 25% packet loss.
        if sent > 0:
            result["packet_loss_percent"] = round(
                ((sent - received) / sent) * 100,
                2
            )

        # Extract individual ping reply times from the output.
        # Examples recognized:
        # "time=12.3 ms"
        # "time<1ms"
        #
        # Each captured number represents a reply's reported latency.
        times = re.findall(
            r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms",
            output,
            re.IGNORECASE,
        )

        # Convert the captured strings into floating-point numbers.
        latencies = [float(value) for value in times]

        # Calculate the minimum, average, and maximum reply latency.
        # These remain None if no reply times were found.
        if latencies:
            result["min_latency_ms"] = round(min(latencies), 2)

            result["avg_latency_ms"] = round(
                sum(latencies) / len(latencies),
                2
            )

            result["max_latency_ms"] = round(max(latencies), 2)

        # Determine whether at least one ping reply was received.
        if received > 0:
            result["status"] = "success"
        else:
            # No replies may mean the host is unreachable, packets are
            # being filtered, or the network is unavailable.
            result["status"] = "failed"
            result["error"] = "No ping replies received"

        # Record an unusual exit code even if some replies were received.
        if completed.returncode != 0 and received > 0:
            result["error"] = (
                "Ping command returned a non-zero exit code"
            )

    # Handle cases where the ping executable is not installed or available.
    except FileNotFoundError:
        result["error"] = "Ping command not found on this system"

    # Handle cases where the overall command takes too long.
    except subprocess.TimeoutExpired:
        result["error"] = "Ping command timed out"

    # Handle other operating-system errors.
    except OSError as exc:
        result["error"] = str(exc)

    # Return all measurements and status information to the caller.
    return result
