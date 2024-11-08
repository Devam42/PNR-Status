import requests
import re
import json
import datetime
import time
from fake_useragent import UserAgent
from threading import Lock
from requests.exceptions import SSLError
from config import REQUEST_TIMEOUT
import logging

tokens = 2
last_request_time = time.time()
lock = Lock()

def get_fake_user_agent_response(url):
    global tokens, last_request_time, lock
    try:
        with lock:
            current_time = time.time()
            time_passed = current_time - last_request_time
            tokens += time_passed
            if tokens > 2:
                tokens = 2

            if tokens >= 1:
                tokens -= 1
            else:
                time_to_wait = 1 - tokens
                time.sleep(time_to_wait)
                tokens = 0

            last_request_time = time.time()

            user_agent = UserAgent()
            random_user_agent = user_agent.random
            headers = {"User-Agent": random_user_agent}
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, verify=True)
            return response, None

    except requests.exceptions.Timeout:
        return None, "The request timed out. Please try again later."
    except SSLError as e:
        return None, f"SSL error occurred: {e}"
    except requests.exceptions.RequestException as e:
        return None, f"An error occurred: {e}"

def get_data(url):
    response, error = get_fake_user_agent_response(url)
    if error:
        return None, error
    if response is None or response.status_code != 200:
        return None, f"Failed to retrieve data from the server. Status code: {response.status_code if response else 'No response'}"
    return response.text, None

def extract_data(html_data, pnr_number):
    try:
        # Adjusted regex pattern to correctly find the JSON data
        json_data_match = re.search(r'data\s*=\s*(\{.*?\});', html_data, re.DOTALL)
        if json_data_match:
            json_str = json_data_match.group(1)
            # Remove any trailing semicolons
            if json_str.endswith(';'):
                json_str = json_str[:-1]
            # Parse the JSON data
            data = json.loads(json_str)
            # Build the response data according to your sample structure
            extracted_data = {
                "Pnr": data.get("Pnr", pnr_number),
                "TrainNo": data.get("TrainNo"),
                "TrainName": data.get("TrainName"),
                "Doj": data.get("Doj"),
                "BookingDate": data.get("BookingDate"),
                "Quota": data.get("Quota"),
                "DestinationDoj": data.get("DestinationDoj"),
                "SourceDoj": data.get("SourceDoj"),
                "From": data.get("From"),
                "FromStnActual": data.get("FromStnActual"),
                "To": data.get("To"),
                "ReservationUpto": data.get("ReservationUpto"),
                "BoardingPoint": data.get("BoardingPoint"),
                "Class": data.get("Class"),
                "ChartPrepared": data.get("ChartPrepared"),
                "BoardingStationName": data.get("BoardingStationName"),
                "TrainStatus": data.get("TrainStatus"),
                "TrainCancelledFlag": data.get("TrainCancelledFlag", False),
                "ReservationUptoName": data.get("ReservationUptoName"),
                "PassengerCount": len(data.get("PassengerStatus", [])),
                "PassengerStatus": data.get("PassengerStatus", []),
                "DepartureTime": data.get("DepartureTime"),
                "ArrivalTime": data.get("ArrivalTime"),
                "ExpectedPlatformNo": data.get("ExpectedPlatformNo"),
                "BookingFare": data.get("BookingFare"),
                "TicketFare": data.get("TicketFare"),
                "CoachPosition": data.get("CoachPosition"),
                "Rating": data.get("Rating"),
                "FoodRating": data.get("FoodRating"),
                "PunctualityRating": data.get("PunctualityRating"),
                "CleanlinessRating": data.get("CleanlinessRating"),
                "SourceName": data.get("SourceName"),
                "DestinationName": data.get("DestinationName"),
                "Duration": data.get("Duration"),
                "RatingCount": data.get("RatingCount"),
                "HasPantry": data.get("HasPantry"),
                "GroupingId": data.get("GroupingId"),
                "OptVikalp": data.get("OptVikalp"),
                "VikalpData": data.get("VikalpData"),
                "VikalpTransferred": data.get("VikalpTransferred"),
                "VikalpTransferredMessage": data.get("VikalpTransferredMessage"),
                "FromDetails": data.get("FromDetails"),
                "ToDetails": data.get("ToDetails"),
                "BoardingPointDetails": data.get("BoardingPointDetails"),
                "ReservationUptoDetails": data.get("ReservationUptoDetails")
            }

            # Ensure nested details are present
            for key in ["FromDetails", "ToDetails", "BoardingPointDetails", "ReservationUptoDetails"]:
                if extracted_data.get(key) is None:
                    extracted_data[key] = {
                        "category": None,
                        "division": None,
                        "latitude": None,
                        "longitude": None,
                        "state": None,
                        "stationCode": extracted_data.get("From") if "From" in key else extracted_data.get("To"),
                        "stationName": extracted_data.get("FromStnActual") if "From" in key else extracted_data.get("ReservationUptoName")
                    }

            return extracted_data
        else:
            raise ValueError("Could not find JSON data in the page.")
    except Exception as e:
        logging.error(f"Error in extract_data: {e}")
        return {"error": str(e)}
