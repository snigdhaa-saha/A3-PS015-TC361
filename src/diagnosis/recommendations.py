"""
recommendations.py
==================

Rule-based troubleshooting recommendations for NetDoctor, part of
the NetSages network diagnosis system.

Purpose:
    Provide practical troubleshooting suggestions based on the
    network problem identified by the diagnosis module.

Note:
    These recommendations are general suggestions. They are not
    guaranteed to resolve every network problem.
"""


# ---------------------------------------------------------------------
# TROUBLESHOOTING RECOMMENDATIONS
# ---------------------------------------------------------------------
# Each key represents a diagnosis label, and its value is a list of
# actions that the user can take to investigate or resolve the issue.
#
# IMPORTANT:
# The diagnosis labels must match the labels produced by the diagnosis
# module. We will verify and align these labels during integration.

RECOMMENDATIONS = {
    # Packet loss can result from unstable Wi-Fi, congestion, or
    # problems along the network path.
    "High Packet Loss": [
        "Check Wi-Fi stability",
        "Move closer to the router",
        "Repeat the network test",
    ],

    # High latency means network responses are taking longer than
    # expected. Congestion and the selected server may contribute.
    "High Latency": [
        "Check network congestion",
        "Test another server",
        "Repeat the test",
    ],

    # A weak wireless signal can result from distance, obstructions,
    # or poor router placement.
    "Weak Wi-Fi Signal": [
        "Move closer to the router",
        "Reposition the router",
        "Check for physical obstructions",
    ],

    # Slow DNS resolution can delay the process of translating domain
    # names into IP addresses.
    "Possible DNS Issue": [
        "Repeat the DNS test",
        "Try another DNS resolver",
    ],
}


# ---------------------------------------------------------------------
# RECOMMENDATION LOOKUP
# ---------------------------------------------------------------------

def get_recommendations(problem):
    """
    Return troubleshooting suggestions for a diagnosed network problem.

    Args:
        problem (str):
            A diagnosis label, such as "High Latency" or
            "Weak Wi-Fi Signal".

    Returns:
        list:
            A list of recommended actions if the diagnosis is known.
            An empty list if the input is invalid or no matching
            recommendations are available.
    """

    # Reject missing or non-string diagnosis labels.
    if not isinstance(problem, str):
        return []

    # Remove accidental whitespace around the supplied label.
    problem = problem.strip()

    # Match labels without being sensitive to capitalization.
    for diagnosis, suggestions in RECOMMENDATIONS.items():
        if problem.casefold() == diagnosis.casefold():
            # Return a copy so callers cannot modify the stored list.
            return suggestions.copy()

    # Avoid inventing recommendations for unknown diagnoses.
    return []


# ---------------------------------------------------------------------
# MANUAL TESTING
# ---------------------------------------------------------------------
# Run this file from the repository's src directory using:
#
#     python diagnosis/recommendations.py

if __name__ == "__main__":

    # Test one known diagnosis and one unsupported diagnosis.
    test_problems = [
        "High Latency",
        "Weak Wi-Fi Signal",
        "Unknown Problem",
    ]

    for problem in test_problems:
        print(f"\nDiagnosis: {problem}")

        suggestions = get_recommendations(problem)

        if suggestions:
            for number, suggestion in enumerate(suggestions, start=1):
                print(f"{number}. {suggestion}")
        else:
            print("No recommendations available.")
