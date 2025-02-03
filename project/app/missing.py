from datetime import timedelta
import pandas as pd


# Function to check for missing 5-minute intervals (adjusted for UTC +5:30)
def find_missing_intervals(data, interval_minutes=5):
    missing_intervals = []
    previous_etm = None

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Adjust the etm time by adding 5 hours and 30 minutes (UTC+5:30)
    df["etm"] = pd.to_datetime(df["data"].apply(lambda x: x["evt"]["etm"]))
    df["etm"] = df["etm"] + timedelta(hours=5, minutes=30)

    # Sort by timestamp
    df = df.sort_values(by="etm")

    # Compare timestamps and check for gaps
    for idx, row in df.iterrows():
        if previous_etm:
            expected_next_etm = previous_etm + timedelta(minutes=interval_minutes) # noqa
            if row["etm"] > expected_next_etm:
                # Calculate missing time intervals
                missing_start = previous_etm + timedelta(minutes=interval_minutes) # noqa
                missing_end = row["etm"]
                while missing_start < missing_end:
                    missing_intervals.append(
                        {
                            "missing_interval_start": missing_start,
                            "missing_interval_end": missing_start
                            + timedelta(minutes=interval_minutes),
                        }
                    )
                    missing_start += timedelta(minutes=interval_minutes)
        previous_etm = row["etm"]

    return missing_intervals
