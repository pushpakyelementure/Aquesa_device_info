import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def display_consumption_chart(data):
    # Ensure `data` is a Pandas DataFrame
    if isinstance(data, list):
        if len(data) == 0:  # Handle empty list case
            st.warning("No data available for the selected range.")
            return
        df = pd.DataFrame(data)  # Convert list to DataFrame
    elif isinstance(data, pd.DataFrame):
        df = data  # Already a DataFrame, use as is
    else:
        st.error("Invalid data format. Expected a list of dictionaries or a DataFrame.") # noqa
        return

    if df.empty:  # Now this check will work
        st.warning("No data available for the selected range.")
        return

    # Convert 'devicetime' to datetime format
    df["devicetime"] = pd.to_datetime(df["devicetime"], errors="coerce")
    df = df.dropna(subset=["devicetime"])
    df["hour"] = df["devicetime"].dt.floor("h")

    # Extract 'csm' from nested 'data' dictionary
    df["csm"] = df["data"].apply(lambda x: x.get("evt", {}).get("csm", 0) if isinstance(x, dict) else 0) # noqa

    # Aggregate hourly consumption
    hourly_consumption = df.groupby("hour")["csm"].sum().reset_index()

    # Plot the bar chart
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(hourly_consumption["hour"].dt.strftime("%H:%M"), hourly_consumption["csm"], color="blue") # noqa

    ax.set_title("Hourly Total Consumption", fontsize=14)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Total Consumption")
    ax.set_xticklabels(hourly_consumption["hour"].dt.strftime("%H:%M"), rotation=45) # noqa

    # Annotate each bar with the consumption value
    for i, value in enumerate(hourly_consumption["csm"]):
        ax.annotate(
            f"{value:.2f}",  # Format the value to 2 decimal places
            (i, value),  # Position the annotation at the bar
            textcoords="offset points",  # Offset from the bar
            xytext=(0, 5),  # Offset by 5 points in the y-direction
            ha="center",  # Horizontal alignment
        )

    # Display the plot in Streamlit
    st.pyplot(fig)
