# data/zone_lookup/

Maps the integer LocationID fields in the NYC TLC trip data (PULocationID,
DOLocationID) to human-readable Borough/Zone names.

**What's here:** `taxi_zone_lookup.csv`, published alongside the TLC trip
data. It's already included, so there's nothing to download.

**Expected columns:** `LocationID`, `Borough`, `Zone`, `service_zone`.

**Used by:** `src/transforms.py` joins these zone names onto every ride, and
the dashboard uses them to label charts.
