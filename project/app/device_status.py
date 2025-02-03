from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
import uuid
import os

# MongoDB connection
db_url = MongoClient(os.getenv("AQUESA_DB_DEV_URI"), uuidRepresentation="standard") # noqa
db = db_url[os.getenv("AQUESA_DB_NAME")]
collection = db[os.getenv("AQS_DEVICE_STATUS")]


# to check device status
def check_device_status(device_id: uuid.UUID):
    device_data = collection.find_one({"deviceid": device_id}, sort=[("timestamp", -1)])  # noqa
    if not device_data:
        raise Exception("Device not found")
    current_time = datetime.now(pytz.utc)
    last_seen = device_data["devicetime"]
    # Convert last_seen to an offset-aware datetime if it is offset-naive
    if last_seen.tzinfo is None or last_seen.tzinfo.utcoffset(last_seen) is None:  # noqa
        last_seen = pytz.utc.localize(last_seen)
    time_diff = (current_time - last_seen).total_seconds()
    if time_diff > 300:
        status = "Inactive"
        inactive_duration = str(timedelta(seconds=time_diff))
    else:
        status = "Active"
        inactive_duration = "0s"

    return {"device_id": device_id, "status": status, "last_seen": last_seen, "inactive_duration": inactive_duration}  # noqa


# Function to simulate an API request (instead of FastAPI)
def get_device_status(device_id: uuid.UUID):
    try:
        status = check_device_status(device_id)
        return status
    except Exception as e:
        return {"Error": str(e)}


# Helper function to check device status
def check_all_devices_status():
    current_time = datetime.now(pytz.utc)
    device_status_list = {}

    # Fetch all latest device statuses
    pipeline = [
        {"$sort": {"deviceid": 1, "timestamp": -1}},  # Sort by device ID and latest timestamp # noqa
        {"$group": {"_id": "$deviceid", "last_seen": {"$first": "$devicetime"}}} # Get the latest record for each device # noqa
    ]

    latest_statuses = collection.aggregate(pipeline)

    # Iterate through each device and check status
    for device in latest_statuses:
        device_id = device["_id"]
        last_seen = device["last_seen"]

        if last_seen.tzinfo is None or last_seen.tzinfo.utcoffset(last_seen) is None:  # noqa
            last_seen = pytz.utc.localize(last_seen)

        time_diff = (current_time - last_seen).total_seconds()
        if time_diff > 300:
            status = "Inactive"
            inactive_duration = str(timedelta(seconds=time_diff))
        else:
            status = "Active"
            inactive_duration = "0s"

        device_status_list[device_id] = {
            "device_id": str(device_id),
            "status": status,
            "last_seen": last_seen,
            "inactive_duration": inactive_duration
        }

    return list(device_status_list.values())


# Function to get all device statuses
def get_all_device_status():
    try:
        status_list = check_all_devices_status()
        return status_list
    except Exception as e:
        return {"Error": str(e)}
