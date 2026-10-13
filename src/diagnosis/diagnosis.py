
"""
diagnosis.py
============

Rule-based network diagnosis module for NetDoctor, developed by
the NetSages team.

Purpose:
    Analyse network measurements, identify suspected connectivity
    problems, and return evidence-backed diagnosis results.

Each diagnosis contains:
    - problem:    Name of the suspected network issue.
    - severity:   Estimated severity of the issue.
    - confidence: Current rule-based confidence label.
    - evidence:   Explanation of the measurement that triggered the rule.

Important:
    The thresholds and confidence labels are initial heuristics.
    They should be validated against representative network data.
"""


def diagnose(metrics):
    """
    Analyse network measurements and identify possible connectivity issues.

    Args:
        metrics (dict):
            A dictionary containing available measurements, for example:
            {
                "packet_loss": 8,
                "latency": 200,
                "wifi_signal": "strong",
                "dns_time": 50,
            }

    Returns:
        list[dict]:
            A list of diagnosis results. Each result contains the problem,
            severity, confidence label, and supporting evidence.

            If measurements are missing, an "Incomplete Measurements"
            result is added to the list.

    Note:
        This function uses fixed rules and confidence labels. It does not
        yet use the scoring function from confidence.py.
    """

    # Reject invalid input instead of failing on .get() calls.
    if not isinstance(metrics, dict):
        raise TypeError("metrics must be a dictionary")

    # Store each diagnosis in this list as the rules are evaluated.
    results = []

    # Extract the measurements used by the current diagnosis rules.
    packet_loss = metrics.get("packet_loss")
    latency = metrics.get("latency")
    wifi_signal = metrics.get("wifi_signal")
    dns_time = metrics.get("dns_time")

    # -------------------------------------------------------------
    # 1. HIGH PACKET LOSS
    # -------------------------------------------------------------
    # Packet loss above 5% may indicate an unstable connection,
    # congestion, wireless interference, or another network problem.

    if packet_loss is not None and packet_loss > 5:
        results.append({
            "problem": "High Packet Loss",
            "severity": "High",
            "confidence": "High",
            "evidence": (
                f"Packet loss is {packet_loss}%, "
                "which exceeds 5%."
            ),
        })

    # -------------------------------------------------------------
    # 2. HIGH LATENCY
    # -------------------------------------------------------------
    # Latency above 150 milliseconds may cause noticeable delays
    # in interactive applications and other network activities.

    if latency is not None and latency > 150:
        results.append({
            "problem": "High Latency",
            "severity": "Medium",
            "confidence": "High",
            "evidence": (
                f"Latency is {latency} ms, "
                "which exceeds 150 ms."
            ),
        })

    # -------------------------------------------------------------
    # 3. WEAK WI-FI SIGNAL
    # -------------------------------------------------------------
    # This rule is based on the categorical Wi-Fi signal value.
    # Normalize the text to handle capitalization and whitespace.

    if isinstance(wifi_signal, str) and wifi_signal.strip().lower() == "weak":
        results.append({
            "problem": "Weak Wi-Fi Signal",
            "severity": "Medium",
            "confidence": "High",
            "evidence": "The measured Wi-Fi signal is weak.",
        })

    # -------------------------------------------------------------
    # 4. POSSIBLE DNS ISSUE
    # -------------------------------------------------------------
    # DNS resolution taking more than 200 milliseconds may contribute
    # to delays when opening websites or connecting to services.
    # A high DNS time alone does not prove that DNS is the root cause.

    if dns_time is not None and dns_time > 200:
        results.append({
            "problem": "Possible DNS Issue",
            "severity": "Medium",
            "confidence": "Medium",
            "evidence": f"DNS resolution took {dns_time} ms.",
        })

    # -------------------------------------------------------------
    # 5. POSSIBLE NETWORK INSTABILITY
    # -------------------------------------------------------------
    # Flag a possible combined issue when both packet loss and latency
    # exceed their configured thresholds.
    #
    # This rule captures a combination of symptoms. It does not prove
    # that the connection is unstable in every circumstance.

    if (
        packet_loss is not None
        and latency is not None
        and packet_loss > 5
        and latency > 150
    ):
        results.append({
            "problem": "Possible Network Instability",
            "severity": "High",
            "confidence": "Medium",
            "evidence": (
                f"Packet loss is {packet_loss}% "
                f"and latency is {latency} ms."
            ),
        })

    # -------------------------------------------------------------
    # 6. CHECK FOR INCOMPLETE MEASUREMENTS
    # -------------------------------------------------------------
    # Record which expected measurements are absent. A missing value
    # is different from a measured value of zero.
    #
    # The current implementation expects all four metrics. If your
    # measurement pipeline intentionally omits a metric, this warning
    # can help explain why the diagnosis may be incomplete.

    missing = []

    if packet_loss is None:
        missing.append("packet_loss")

    if latency is None:
        missing.append("latency")

    if wifi_signal is None:
        missing.append("wifi_signal")

    if dns_time is None:
        missing.append("dns_time")

    # Add a warning only when one or more expected measurements are absent.
    if missing:
        results.append({
            "problem": "Incomplete Measurements",
            "severity": "Low",
            "confidence": "High",
            "evidence": (
                f"Missing measurements: {', '.join(missing)}"
            ),
        })

    # Return all identified problems and warnings to the calling module.
    return results


# ---------------------------------------------------------------------
# MANUAL TESTING
# ---------------------------------------------------------------------
# Run from the repository's src directory:
#
#     python diagnosis/diagnosis.py
#
# These examples verify the diagnosis rules without requiring a live
# network connection.

if __name__ == "__main__":

    # Example measurements that should trigger multiple diagnosis rules.
    sample_metrics = {
        "packet_loss": 8,
        "latency": 200,
        "wifi_signal": "strong",
        "dns_time": 50,
    }

    print("NetSages | NetDoctor Diagnosis Results")
    print("-" * 42)

    # Run the diagnosis function on the sample data.
    sample_results = diagnose(sample_metrics)

    # Print each diagnosis in a readable format.
    for result in sample_results:
        print(f"\nProblem: {result['problem']}")
        print(f"Severity: {result['severity']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Evidence: {result['evidence']}")
