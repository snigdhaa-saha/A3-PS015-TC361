
"""
NetSages | NetDoctor
Streamlit dashboard for explainable home and last-mile
Internet connectivity diagnosis.
"""

# ============================================================
# 1. IMPORT DEPENDENCIES
# ============================================================

try:
    import streamlit as st
except ModuleNotFoundError:
    raise SystemExit(
        "Streamlit is missing. Install it in your virtual "
        "environment before launching the dashboard."
    )

try:
    import pandas as pd
except ModuleNotFoundError:
    raise SystemExit(
        "Pandas is missing. Install it in your virtual "
        "environment before launching the dashboard."
    )

# Import the existing diagnosis engine and recommendations.
from diagnosis import diagnose
from recommendations import RECOMMENDATIONS


# ============================================================
# 2. PAGE CONFIGURATION
# ============================================================

# Keep page configuration at the top, before other Streamlit
# elements. Do not put captions or headings inside this block.
st.set_page_config(
    page_title="NetDoctor | NetSages",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 3. CUSTOM CSS STYLING
# ============================================================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 0;
            letter-spacing: -1px;
        }

        .team-name {
            font-size: 17px;
            color: #55B9FF;
            margin-top: 2px;
            margin-bottom: 8px;
        }

        .subtitle {
            font-size: 16px;
            color: #94A3B8;
            margin-top: 8px;
            margin-bottom: 22px;
        }

        .section-title {
            font-size: 24px;
            font-weight: 700;
            margin-top: 22px;
            margin-bottom: 12px;
        }

        .project-label {
            font-size: 13px;
            color: #94A3B8;
            margin-top: 0;
            margin-bottom: 18px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 4. DASHBOARD HEADER
# ============================================================

# NetDoctor is the product name.
st.markdown(
    '<div class="main-title">🌐 NetDoctor</div>',
    unsafe_allow_html=True,
)

# NetSages is the team responsible for the project.
st.markdown(
    '<div class="team-name">by NetSages</div>',
    unsafe_allow_html=True,
)

# Explain the application's purpose.
st.markdown(
    '<div class="subtitle">'
    'Explainable Home and Last-Mile Internet Connectivity Diagnosis'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="project-label">AIORI3 Hackathon Project</div>',
    unsafe_allow_html=True,
)

st.info(
    "Enter network measurements to identify potential connectivity "
    "problems and understand the evidence behind each finding."
)


# ============================================================
# 5. SIDEBAR: NETWORK MEASUREMENT INPUTS
# ============================================================

st.sidebar.header("Network Measurements")

st.sidebar.caption(
    "Use illustrative demo values or enter your own measurements."
)

# Demo mode is enabled by default so the dashboard is ready to
# demonstrate immediately after launch.
demo_mode = st.sidebar.checkbox(
    "Use illustrative demo values",
    value=True,
)

if demo_mode:
    # These values are synthetic examples, not live measurements.
    latency = 200.0
    packet_loss = 8.0
    wifi_signal = "strong"
    dns_time = 50.0

    st.sidebar.info(
        "Demo mode is active. All displayed values are illustrative."
    )

else:
    # Allow the user to enter latency in milliseconds.
    latency = st.sidebar.number_input(
        "Latency (ms)",
        min_value=0.0,
        max_value=60000.0,
        value=50.0,
        step=1.0,
    )

    # Packet loss is represented as a percentage.
    packet_loss = st.sidebar.number_input(
        "Packet Loss (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.5,
    )

    # Choose a Wi-Fi signal category.
    wifi_signal = st.sidebar.selectbox(
        "Wi-Fi Signal",
        ["strong", "medium", "weak", "unknown"],
    )

    # DNS resolution time is measured in milliseconds.
    dns_time = st.sidebar.number_input(
        "DNS Resolution Time (ms)",
        min_value=0.0,
        max_value=60000.0,
        value=30.0,
        step=1.0,
    )


# ============================================================
# 6. PREPARE THE MEASUREMENT DATA
# ============================================================

# Represent an unknown Wi-Fi signal as None so the diagnosis
# engine does not mistake it for a measured signal.
network_data = {
    "latency": latency,
    "packet_loss": packet_loss,
    "wifi_signal": (
        None if wifi_signal == "unknown" else wifi_signal
    ),
    "dns_time": dns_time,
}


# ============================================================
# 7. RUN THE DIAGNOSIS ENGINE
# ============================================================

# Use the existing project diagnosis engine.
results = diagnose(network_data)

# Separate network problems from incomplete-data warnings.
problem_results = [
    result
    for result in results
    if result["problem"] != "Incomplete Measurements"
]

incomplete_results = [
    result
    for result in results
    if result["problem"] == "Incomplete Measurements"
]


# ============================================================
# 8. NETWORK OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">Network Overview</div>',
    unsafe_allow_html=True,
)

# Display the four current measurement values.
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Latency",
    f"{latency:.1f} ms",
)

col2.metric(
    "Packet Loss",
    f"{packet_loss:.1f}%",
)

col3.metric(
    "DNS Resolution",
    f"{dns_time:.1f} ms",
)

col4.metric(
    "Wi-Fi Signal",
    wifi_signal.title(),
)


# ============================================================
# 9. DIAGNOSTIC FINDINGS
# ============================================================

st.markdown(
    '<div class="section-title">Diagnosis Results</div>',
    unsafe_allow_html=True,
)

if not problem_results:
    st.success(
        "No issues were flagged by the current diagnostic rules. "
        "This does not guarantee that the connection is problem-free."
    )

else:
    st.write(
        f"**{len(problem_results)} diagnostic finding(s) detected.**"
    )

    # Display each finding with evidence and suggested next steps.
    for result in problem_results:
        problem = result["problem"]
        severity = result["severity"]
        confidence = result.get("confidence", "Unknown")
        evidence = result.get("evidence", "No evidence provided.")

        with st.container(border=True):
            # Use a visible status indicator for the severity.
            if severity == "High":
                st.error(f"🔴 {problem}")
            elif severity == "Medium":
                st.warning(f"🟠 {problem}")
            else:
                st.info(f"🔵 {problem}")

            st.write(f"**Severity:** {severity}")
            st.write(f"**Evidence assessment:** {confidence}")
            st.write(f"**Supporting evidence:** {evidence}")

            st.caption(
                "This finding follows the configured diagnostic "
                "rules. It indicates a potential issue, not proof "
                "of its underlying root cause."
            )

            # Match recommendations without depending on the exact
            # capitalization of the diagnosis label.
            recommendations = next(
                (
                    items
                    for name, items in RECOMMENDATIONS.items()
                    if name.casefold() == problem.casefold()
                ),
                [
                    "Repeat the network measurements.",
                    "Compare results across different destinations.",
                    "Investigate further before assigning a root cause.",
                ],
            )

            st.write("**Recommended next steps:**")

            for recommendation in recommendations:
                st.markdown(f"- {recommendation}")


# ============================================================
# 10. INCOMPLETE MEASUREMENTS
# ============================================================

# Display data-quality warnings separately from network problems.
for result in incomplete_results:
    st.warning(
        f"{result['problem']}: {result['evidence']}"
    )


# ============================================================
# 11. MEASUREMENT DETAILS
# ============================================================

st.markdown(
    '<div class="section-title">Measurement Details</div>',
    unsafe_allow_html=True,
)

# Build a readable table of the values supplied to the diagnosis
# engine. These are input values, not necessarily live measurements.
measurement_table = pd.DataFrame(
    [
        {
            "Measurement": "Latency",
            "Value": f"{latency:.1f} ms",
        },
        {
            "Measurement": "Packet Loss",
            "Value": f"{packet_loss:.1f}%",
        },
        {
            "Measurement": "Wi-Fi Signal",
            "Value": wifi_signal.title(),
        },
        {
            "Measurement": "DNS Resolution",
            "Value": f"{dns_time:.1f} ms",
        },
    ]
)

st.dataframe(
    measurement_table,
    width="stretch",
    hide_index=True,
)


# ============================================================
# 12. EXPLAINABILITY
# ============================================================

st.markdown(
    '<div class="section-title">How the Diagnosis Works</div>',
    unsafe_allow_html=True,
)

st.write(
    "NetDoctor evaluates the supplied measurements against "
    "configured diagnostic rules. Each finding includes the evidence "
    "that triggered the rule, helping users understand why a potential "
    "connectivity problem was flagged."
)

st.write(
    "Multiple findings can occur together. For example, high latency "
    "and packet loss can indicate degraded network performance. "
    "Additional measurements may be needed to distinguish Wi-Fi "
    "interference, congestion, routing problems, and other causes."
)


# ============================================================
# 13. FOOTER
# ============================================================

st.divider()

st.caption(
    "NetDoctor — Explainable Network Diagnosis"
)

st.caption(
    "by NetSages | AIORI3 Hackathon Project"
)

st.caption(
    "Demo measurements are illustrative. Results depend on the "
    "supplied measurements and the configured diagnostic rules."
)
