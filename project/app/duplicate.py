import pandas as pd


# Function to find duplicates
def find_duplicates(data):
    if not data:
        return pd.DataFrame()  # Return empty DataFrame if no data
    df = pd.DataFrame(data)
    # Convert time for better display
    df["devicetime"] = pd.to_datetime(df["devicetime"])

    # Find duplicates based on 'deviceid' and 'devicetime'
    duplicate_df = df[df.duplicated(subset=["deviceid", "devicetime"], keep=False)] # noqa

    return duplicate_df
