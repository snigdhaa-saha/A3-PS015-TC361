"""
main.py
=======

Standalone test runner for NetDoctor's diagnosis module.

Purpose:
    Supply sample network measurements to the diagnose() function
    and print the resulting diagnosis output.

Note:
    This file assumes that diagnosis.py defines a function named
    diagnose() and that it accepts a dictionary of measurements.
"""


# Import the diagnosis function from the diagnosis module.
from diagnosis import diagnose


# ---------------------------------------------------------------------
# SAMPLE NETWORK MEASUREMENTS
# ---------------------------------------------------------------------
# These values simulate one set of network measurements.
#
# latency     : Round-trip latency in milliseconds.
# packet_loss : Percentage of packets lost, from 0 to 100.
# wifi_signal : Wi-Fi signal category.
# dns_time    : DNS resolution time in milliseconds.
#
# These are sample values, not measurements collected from a live
# network connection.

network_data = {
    "latency": 200,
    "packet_loss": 8,
    "wifi_signal": "strong",
    "dns_time": 50,
}


# ---------------------------------------------------------------------
# RUN THE DIAGNOSIS
# ---------------------------------------------------------------------
# Pass the sample measurements to the diagnosis function.
# The returned results may contain one or more identified problems.

results = diagnose(network_data)


# ---------------------------------------------------------------------
# DISPLAY THE RESULTS
# ---------------------------------------------------------------------
# Print each diagnosis returned by the function.
# The exact output depends on the implementation of diagnose().

print("NetSages | NetDoctor Diagnosis Results")
print("-" * 30)

for result in results:
    print(result)
