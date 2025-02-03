import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import uuid
import os
from bson import Binary, UuidRepresentation


def get_data_from_mongodb(device_id, start_date, end_date):
    # MongoDB connection
    db_url = MongoClient(os.getenv("AQUESA_DB_DEV_URI"), uuidRepresentation="standard") # noqa
    db = db_url[os.getenv("AQUESA_DB_NAME")]
    collection = db[os.getenv("RAW_DATA_TS")]

    # Convert device_id to UUID and Binary format
    try:
        device_id_uuid = uuid.UUID(device_id)
        device_id_binary = Binary.from_uuid(device_id_uuid, UuidRepresentation.STANDARD) # noqa
    except ValueError:
        st.error("Invalid Device ID format. Please enter a valid UUID.")
        return []

    # Convert date strings to datetime format
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        st.error("Invalid Date Format. Please use YYYY-MM-DD HH:MM:SS")
        return []

    # Query using the correct UUID format
    query = {
        "deviceid": device_id_binary,
        "devicetime": {"$gte": start_date, "$lte": end_date}
    }

    # Projection to fetch only required fields
    projection = {
        "_id": 0,
        "deviceid": 1,
        "devicetime": 1,
        "data.evt.etm": 1,
        "data.evt.csm": 1
    }

    # Fetch data
    items = list(collection.find(query, projection))
    return items
