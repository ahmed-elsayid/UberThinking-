"""
5_streaming_monitor.py
------------------------
Purpose:
    Dashboard page showing "live" streaming health/activity — closest
    thing to a real-time monitor within Streamlit's request/response model.

Responsibilities:
    - Periodically (e.g. via st.rerun on a timer, or a manual refresh
      button) reload the latest aggregate metrics.
    - Display: incoming ride count (recent window), current revenue
      (recent window), trips per minute, and the most recent ride record.

Expected input:
    - Latest rows from output/parquet/aggregates/ and output/parquet/rides/.

Expected output:
    - Rendered Streamlit page with near-real-time metrics.

Dependencies:
    - streamlit
    - pandas

Note:
    Streamlit is not a true streaming UI framework; document this
    limitation and the chosen refresh strategy (polling interval, manual
    refresh button, or st.autorefresh via a community component) in
    docs/architecture.md.
"""

# TODO: implement periodic/refresh-based loading of latest metrics.
