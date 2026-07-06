"""
1_overview.py
-------------
Purpose:
    Dashboard page showing high-level KPIs and charts summarizing overall
    ride activity.

Responsibilities:
    - Read aggregated metrics from output/parquet/aggregates/ (written by
      streaming/spark_stream_consumer.py + analytics/analytics.py).
    - Display KPI cards: Total Trips, Total Revenue, Average Fare,
      Average Ride Duration.
    - Display charts (via Plotly):
        - Trips per hour
        - Revenue per hour
        - Payment type pie chart
        - Peak hours bar chart

Expected input:
    - Parquet files under output/parquet/aggregates/.

Expected output:
    - Rendered Streamlit page with metrics + charts.

Dependencies:
    - streamlit, plotly.express (or plotly.graph_objects)
    - pandas (for reading Parquet into a small in-memory frame for display)
"""

# TODO: load aggregates -> render st.metric(...) cards + plotly charts.
