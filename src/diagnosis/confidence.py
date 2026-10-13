
"""
confidence.py
==============

Rule-based confidence scoring for NetDoctor, part of the NetSages
network diagnosis system.

Purpose:
    Estimate how strongly a measured network metric supports a
    suspected network problem.

Important:
    The returned score is a heuristic score, NOT a calibrated
    statistical probability. The thresholds and scores are initial
    rules and should be validated against representative network data.
"""

from math import isfinite


# ---------------------------------------------------------------------
# 1. CONFIDENCE LEVEL THRESHOLDS
# ---------------------------------------------------------------------
# Scores at or above these values are assigned readable confidence
# labels. These labels describe the heuristic score, not certainty.

HIGH_THRESHOLD = 0.80
MEDIUM_THRESHOLD = 0.50


# ---------------------------------------------------------------------
# 2. DIAGNOSIS RULES
# ---------------------------------------------------------------------
# Each supported diagnosis maps to a measurement metric and a list
# of (threshold, score) pairs.
#
# Assumed measurement units:
#   latency    : milliseconds
#   packet_loss: percentage, from 0 to 100
#   dns_time   : milliseconds
#
# For "greater_than", thresholds are checked from highest to lowest.
# For example, latency above 300 ms receives a score of 0.95.
#
# These are configurable starting values, not universal standards.

DIAGNOSIS_RULES = {
    "high_latency": {
        "metric": "latency",
        "thresholds": [
            (300, 0.95),
            (150, 0.85),
            (100, 0.60),
        ],
        "comparison": "greater_than",
    },
    "packet_loss": {
        "metric": "packet_loss",
        "thresholds": [
            (10, 0.95),
            (5, 0.85),
            (2, 0.60),
        ],
        "comparison": "greater_than",
    },
    "weak_wifi": {
        "metric": "wifi_signal",
        "thresholds": [],
        "comparison": "categorical",
    },
    "dns_issue": {
        "metric": "dns_time",
        "thresholds": [
            (500, 0.95),
            (200, 0.85),
            (100, 0.60),
        ],
        "comparison": "greater_than",
    },
}


# ---------------------------------------------------------------------
# 3. DIAGNOSIS LABEL ALIASES
# ---------------------------------------------------------------------
# Different modules or CSV files may use different spellings for
# the same diagnosis. Map known alternatives to a canonical label.
#
# This allows labels such as "High Latency" and "high_latency" to
# be processed consistently.

ALIASES = {
    "high latency": "high_latency",
    "high_latency": "high_latency",
    "packet loss": "packet_loss",
    "high packet loss": "packet_loss",
    "packet_loss": "packet_loss",
    "weak wifi": "weak_wifi",
    "weak wi-fi": "weak_wifi",
    "weak wifi signal": "weak_wifi",
    "weak_wifi": "weak_wifi",
    "possible dns issue": "dns_issue",
    "dns issue": "dns_issue",
    "dns_issue": "dns_issue",
    "network instability": "network_instability",
    "network_instability": "network_instability",
    "normal": "normal",
}


# ---------------------------------------------------------------------
# 4. HELPER FUNCTIONS
# ---------------------------------------------------------------------

def _normalise_problem(problem):
    """
    Convert a diagnosis label to a consistent format.

    Args:
        problem: The diagnosis label supplied by another module.

    Returns:
        A canonical diagnosis label, or None if the input is not a
        string.
    """
    if not isinstance(problem, str):
        return None

    # Remove surrounding whitespace and ignore capitalization.
    label = problem.strip().lower()

    # Resolve known aliases. For other labels, replace hyphens with
    # underscores to support a consistent naming convention.
    return ALIASES.get(label, label.replace("-", "_"))


def _valid_number(value):
    """
    Check whether a measurement is a finite integer or float.

    Boolean values are explicitly rejected because Python treats
    bool as a subclass of int.

    Rejecting NaN and infinity prevents invalid comparisons from
    producing misleading confidence scores.
    """
    if isinstance(value, bool):
        return False

    if not isinstance(value, (int, float)):
        return False

    return isfinite(value)


def _get_level(score):
    """
    Convert a numeric heuristic score into a readable confidence level.

    Args:
        score: A numeric score between 0 and 1.

    Returns:
        "High", "Medium", or "Low".
    """
    if score >= HIGH_THRESHOLD:
        return "High"

    if score >= MEDIUM_THRESHOLD:
        return "Medium"

    return "Low"


# ---------------------------------------------------------------------
# 5. MAIN CONFIDENCE CALCULATION
# ---------------------------------------------------------------------

def calculate_confidence(metrics, problem):
    """
    Calculate heuristic confidence for a suspected network problem.

    Args:
        metrics (dict):
            Network measurements, for example:
            {
                "latency": 180,
                "packet_loss": 1,
                "wifi_signal": "strong",
                "dns_time": 35,
            }

        problem (str):
            The suspected diagnosis, such as "high_latency",
            "packet_loss", "weak_wifi", or "dns_issue".

    Returns:
        tuple:
            (score, level)

            score:
                A float between 0 and 1, or None if the score cannot
                be evaluated because the diagnosis or measurement
                is unsupported, missing, or invalid.

            level:
                "High", "Medium", "Low", or "Unknown".

    Notes:
        A score of zero means the configured rule does not support
        the suspected problem. It does not prove the network is
        functioning correctly.
    """

    # Validate the container before attempting dictionary operations.
    if not isinstance(metrics, dict):
        return None, "Unknown"

    # Normalize the supplied diagnosis label.
    diagnosis = _normalise_problem(problem)

    # A missing or unsupported label cannot be scored reliably.
    if diagnosis is None or diagnosis not in DIAGNOSIS_RULES:
        # "normal" is not a fault diagnosis. "network_instability"
        # also requires a dedicated multi-metric rule.
        return None, "Unknown"

    # Retrieve the measurement name associated with this diagnosis.
    rule = DIAGNOSIS_RULES[diagnosis]
    metric_name = rule["metric"]
    value = metrics.get(metric_name)

    # A missing measurement cannot support a confidence calculation.
    if value is None:
        return None, "Unknown"

    # -------------------------------------------------------------
    # 5A. CATEGORICAL WIFI SIGNAL EVALUATION
    # -------------------------------------------------------------
    # Wi-Fi signal strength is represented by text rather than a
    # numeric measurement in the current input format.

    if diagnosis == "weak_wifi":

        # Reject unexpected input types.
        if not isinstance(value, str):
            return None, "Unknown"

        signal = value.strip().lower()

        # Assign heuristic scores according to the supplied category.
        if signal == "weak":
            score = 0.90
        elif signal == "medium":
            score = 0.50
        elif signal in {"strong", "good"}:
            score = 0.0
        else:
            # Unknown categories must not be treated as valid data.
            return None, "Unknown"

        return score, _get_level(score)

    # -------------------------------------------------------------
    # 5B. NUMERIC MEASUREMENT VALIDATION
    # -------------------------------------------------------------
    # Latency, packet loss, and DNS time must be finite, non-negative
    # numeric values. Strings, booleans, NaN, infinity, and negative
    # values are rejected.

    if not _valid_number(value) or value < 0:
        return None, "Unknown"

    # Packet loss is a percentage and cannot exceed 100%.
    if diagnosis == "packet_loss" and value > 100:
        return None, "Unknown"

    # -------------------------------------------------------------
    # 5C. THRESHOLD-BASED SCORING
    # -------------------------------------------------------------
    # Check thresholds from highest to lowest. Return the score
    # associated with the first threshold exceeded.
    #
    # Example:
    #   latency = 180 ms
    #   180 is not greater than 300, but it is greater than 150.
    #   Therefore, the heuristic score is 0.85 (High).

    for threshold, score in rule["thresholds"]:
        if value > threshold:
            return score, _get_level(score)

    # None of the configured thresholds was exceeded. Return zero
    # to indicate that this rule does not support the suspected fault.
    return 0.0, "Low"


# ---------------------------------------------------------------------
# 6. MANUAL TEST EXAMPLES
# ---------------------------------------------------------------------
# Running this file directly executes these examples:
#
#     python src/diagnosis/confidence.py
#
# These examples provide basic checks of normal operation, missing
# measurements, invalid values, and unsupported diagnosis labels.
# They are not a replacement for the project's automated test suite.

if __name__ == "__main__":

    examples = [
        (
            {
                "latency": 180,
                "packet_loss": 1,
                "wifi_signal": "strong",
                "dns_time": 35,
            },
            "high_latency",
        ),
        ({"packet_loss": 8}, "packet_loss"),
        ({"wifi_signal": "weak"}, "weak_wifi"),
        ({"dns_time": 300}, "dns_issue"),
        ({}, "high_latency"),
        ({"latency": -10}, "high_latency"),
        ({"latency": 180}, "unsupported_problem"),
    ]

    # Evaluate each example and display its score and confidence label.
    for metrics, problem in examples:
        score, level = calculate_confidence(metrics, problem)

        print(
            f"Problem: {problem:22} "
            f"Score: {str(score):5} "
            f"Level: {level}"
        )
