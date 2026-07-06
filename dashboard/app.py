"""
app.py
------
Purpose:
    Entry point for the Streamlit multipage dashboard. Streamlit
    automatically turns every file in dashboard/pages/ into a page in the
    sidebar navigation, so this file mainly sets shared/global config and
    a landing screen.

Responsibilities:
    - st.set_page_config(...) — title, icon, wide layout.
    - Display a short welcome/landing message describing the app and
      linking to each page (Overview, Location Analytics, Ride Explorer,
      Prediction, Streaming Monitor).
    - Initialize any shared resources needed across pages (e.g. a cached
      Spark session or cached data-loading functions), typically via
      @st.cache_resource / @st.cache_data helper functions defined here or
      in a shared utils module.

Expected input:
    - None directly; pages read from output/parquet/ and models/.

Expected output:
    - Rendered Streamlit landing page.

Dependencies:
    - streamlit
    - config/config.py

Run:
    streamlit run dashboard/app.py
"""

# TODO: st.set_page_config(...); render landing content.
