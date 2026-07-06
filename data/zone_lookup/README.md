# data/zone_lookup/

Purpose:
    Maps the integer LocationID fields in the NYC TLC trip data
    (PULocationID, DOLocationID) to human-readable Borough/Zone names.

What goes here:
    - taxi_zone_lookup.csv, published alongside the TLC trip data.

Expected columns:
    - LocationID
    - Borough
    - Zone
    - service_zone

Used by:
    - preprocessing/cleaning.py   (to join zone names onto each ride)
    - analytics/analytics.py      (to group aggregations by zone/borough)
    - dashboard/pages/2_location_analytics.py (to label charts/maps)
