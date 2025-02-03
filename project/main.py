import streamlit as st
import uuid
from streamlit_option_menu import option_menu
from app.device_status import get_device_status, get_all_device_status
from app.fetch_data import get_data_from_mongodb
from app.graph import display_consumption_chart
from app.duplicate import find_duplicates
from app.missing import find_missing_intervals
import pandas as pd

# Streamlit UI
with st.sidebar:
    selected = option_menu(
        menu_title="Device Info",
        options=["Get Data", "Generate Graph", "Check Device Status", "Check All Device Status", "Check Duplicate data", "Check Missing Data"], # noqa
        icons=["download", "bar-chart", "activity", "activity" ,"exclamation-triangle", "file-earmark-minus"], # noqa        
        menu_icon="cast",
        default_index=0,
    )

if selected == "Check Device Status":
    st.title("Check One Device Status Data")

    device_id = st.text_input("Enter Device ID (UUID format)")
    if st.button("Submit"):
        try:
            # Validate and parse UUID
            device_uuid = uuid.UUID(device_id)
            status = get_device_status(device_uuid)
            st.write(status)
            # Display only the status (Active/Inactive) and inactive duration if applicable # noqa
            if status["status"] == "Active":
                st.success("Device Status: Active")
            else:
                st.error(f"Device Status: Inactive for {status['inactive_duration']}") # noqa

        except ValueError:
            st.error("Invalid UUID format. Please enter a valid UUID.")


# ✅ Check all device statuses
if selected == "Check All Device Status":
    st.title("Check All Device Status Data")

    # Function to apply color formatting
    def color_status(val):
        if val == "Active":
            return "color: green; font-weight: bold;"  # Green text for Active
        elif val == "Inactive":
            return "color: red; font-weight: bold;"  # Red text for Inactive
        return ""

    if st.button("Fetch All Device Status"):
        try:
            all_status = get_all_device_status()  # Fetch all device statuses

            # Convert to DataFrame for better visualization
            df = pd.DataFrame(all_status)
            styled_df = df.style.map(color_status, subset=["status"])

            st.dataframe(styled_df)

        except Exception as e:
            st.error(f"Error fetching device status: {e}")


elif selected == "Get Data":
    st.title("Fetch One Device Data")

    device_id = st.text_input("Enter Device ID (UUID format)")
    start_date = st.text_input("Enter Start Date (YYYY-MM-DD HH:MM:SS)")
    end_date = st.text_input("Enter End Date (YYYY-MM-DD HH:MM:SS)")

    # Submit button
    if st.button("Submit"):
        # Fetch data from MongoDB
        data = get_data_from_mongodb(device_id, start_date, end_date)

        if data:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df["devicetime"] = pd.to_datetime(df["devicetime"])

            st.success(f"Found {len(df)} records!")
            st.dataframe(df)  # Display in a table format
        else:
            st.warning("No data found for the given inputs.")


elif selected == "Generate Graph":
    st.title("Generate the Graph of Consumption")

    device_id = st.text_input("Enter Device ID (UUID format)")
    start_date = st.text_input("Enter Start Date (YYYY-MM-DD HH:MM:SS)")
    end_date = st.text_input("Enter End Date (YYYY-MM-DD HH:MM:SS)")
    # Submit button
    if st.button("Submit"):
        # Fetch data from MongoDB
        data = get_data_from_mongodb(device_id, start_date, end_date)

        data1 = display_consumption_chart(data)

    else:
        st.warning("No data found for the given inputs.")

elif selected == "Check Duplicate data":
    st.title("Check Duplicate Data")
    device_id = st.text_input("Enter Device ID (UUID format)")
    start_date = st.text_input("Enter Start Date (YYYY-MM-DD HH:MM:SS)")
    end_date = st.text_input("Enter End Date (YYYY-MM-DD HH:MM:SS)")
    # Submit button
    if st.button("Submit"):
        data = get_data_from_mongodb(device_id, start_date, end_date)

        if data:
            duplicate_data = find_duplicates(data)

            if not duplicate_data.empty:
                st.success(f"Found {len(duplicate_data)} duplicate records!")
                st.dataframe(duplicate_data)  # Display in a table format
            else:
                st.warning("No duplicate records found.")
    else:
        st.warning("No data found for the given inputs.")

elif selected == "Check Missing Data":
    st.title("Check Missing Data")

    device_id = st.text_input("Enter Device ID (UUID format)")
    start_date = st.text_input("Enter Start Date (YYYY-MM-DD HH:MM:SS)")
    end_date = st.text_input("Enter End Date (YYYY-MM-DD HH:MM:SS)")
    # Submit button
    if st.button("Submit"):
        data = get_data_from_mongodb(device_id, start_date, end_date)
        # Checking for missing 5-minute intervals
        missing_intervals = find_missing_intervals(data, interval_minutes=5)

        if missing_intervals:
            st.success(f"Found {len(missing_intervals)} missing data intervals!") # noqa
            # Display missing intervals in a table
            missing_df = pd.DataFrame(missing_intervals)
            st.dataframe(missing_df)
        else:
            st.warning("No missing data found.")
