import json
import logging
import os
from datetime import datetime, timedelta
from time import gmtime, strftime
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename='iotesla.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

global myemail

myemail = os.getenv("MYEMAIL")


def tou_json(input_json):
    logger.info("Generating TOU settings from input JSON")

    # Load input JSON data
    input_data = json.loads(input_json)

    # Extract start and end datetimes
    start_dt_str = input_data[0]["startDt"]
    end_dt_str = input_data[0]["endDt"]

    start_dt = datetime.fromisoformat(start_dt_str)
    end_dt = datetime.fromisoformat(end_dt_str)

    # Calculate the time difference
    time_difference = end_dt - start_dt

    date1 = start_dt.date()
    date2 = end_dt.date()

    if (date2 - date1).days >= 1:
        logger.info("Generating overnight TOU settings (start: %s, end: %s)", start_dt.strftime("%H:%M"), end_dt.strftime("%H:%M"))
        output_json = {
            "OFF_PEAK": [
                {
                    "toMinute": end_dt.minute,
                    "toDayOfWeek": 6,
                    "toHour": end_dt.hour,
                    "fromHour": 0,
                    "fromMinute": 0,
                    "fromDayOfWeek": 0
                },
                {
                    "toMinute": 0,
                    "toDayOfWeek": 6,
                    "toHour": 0,
                    "fromHour": start_dt.hour,
                    "fromMinute": start_dt.minute,
                    "fromDayOfWeek": 0
                }
            ],
            "ON_PEAK": [
                {
                    "fromDayOfWeek": 0,
                    "toDayOfWeek": 6,
                    "fromHour": end_dt.hour,
                    "fromMinute": end_dt.minute,
                    "toHour": start_dt.hour,
                    "toMinute": start_dt.minute
                }
            ]
        }
    elif start_dt == end_dt:
        logger.info("Start and end times are identical, no OFF_PEAK period")
        output_json = {
            "OFF_PEAK": [],
            "ON_PEAK": [
                {
                    "fromDayOfWeek": 0,
                    "toDayOfWeek": 6,
                    "fromHour": 0,
                    "fromMinute": 0,
                    "toHour": 0,
                    "toMinute": 0
                }
            ]
        }
    elif start_dt.hour < 5 or (start_dt.hour == 5 and start_dt.minute < 30):
        logger.info("Generating TOU settings (start before 05:30: %s, end: %s)", start_dt.strftime("%H:%M"), end_dt.strftime("%H:%M"))
        output_json = {
            "OFF_PEAK": [
                {
                    "toMinute": end_dt.minute,
                    "toDayOfWeek": 6,
                    "toHour": end_dt.hour,
                    "fromHour": 0,
                    "fromMinute": 0,
                    "fromDayOfWeek": 0
                },
                {
                    "toMinute": 0,
                    "toDayOfWeek": 6,
                    "toHour": 0,
                    "fromHour": 23,
                    "fromMinute": 30,
                    "fromDayOfWeek": 0
                }
            ],
            "ON_PEAK": [
                {
                    "fromDayOfWeek": 0,
                    "toDayOfWeek": 6,
                    "fromHour": 5,
                    "fromMinute": 30,
                    "toHour": 23,
                    "toMinute": 30
                }
            ]
        }
    elif end_dt.hour == 23 and end_dt.minute >= 30:
        logger.info("Generating TOU settings (end at or after 23:30: %s, start: %s)", end_dt.strftime("%H:%M"), start_dt.strftime("%H:%M"))
        output_json = {
            "OFF_PEAK": [
                {
                    "toMinute": 30,
                    "toDayOfWeek": 6,
                    "toHour": 5,
                    "fromHour": 0,
                    "fromMinute": 0,
                    "fromDayOfWeek": 0
                },
                {
                    "toMinute": end_dt.minute,
                    "toDayOfWeek": 6,
                    "toHour": end_dt.hour,
                    "fromHour": start_dt.hour,
                    "fromMinute": start_dt.minute,
                    "fromDayOfWeek": 0
                },
                {
                    "toMinute": 0,
                    "toDayOfWeek": 6,
                    "toHour": 0,
                    "fromHour": 23,
                    "fromMinute": 30,
                    "fromDayOfWeek": 0
                }
            ],
            "ON_PEAK": [
                {
                    "fromDayOfWeek": 0,
                    "toDayOfWeek": 6,
                    "fromHour": 5,
                    "fromMinute": 30,
                    "toHour": start_dt.hour,
                    "toMinute": start_dt.minute
                }
            ]
        }
    else:
        logger.info("Generating TOU settings (standard: %s to %s)", start_dt.strftime("%H:%M"), start_dt.strftime("%H:%M"))
        output_json = {
            "OFF_PEAK": [
                {
                    "toMinute": 30,
                    "toDayOfWeek": 6,
                    "toHour": 5,
                    "fromHour": 0,
                    "fromMinute": 0,
                    "fromDayOfWeek": 0
                },
                {
                    "toMinute": end_dt.minute,
                    "toDayOfWeek": 6,
                    "toHour": end_dt.hour,
                    "fromHour": start_dt.hour,
                    "fromMinute": start_dt.minute,
                    "fromDayOfWeek": 0
                },
                {
                    "toMinute": 0,
                    "toDayOfWeek": 6,
                    "toHour": 0,
                    "fromHour": 23,
                    "fromMinute": 30,
                    "fromDayOfWeek": 0
                }
            ],
            "ON_PEAK": [
                {
                    "fromDayOfWeek": 0,
                    "toDayOfWeek": 6,
                    "fromHour": 5,
                    "fromMinute": 30,
                    "toHour": start_dt.hour,
                    "toMinute": start_dt.minute
                },
                {
                    "fromDayOfWeek": 0,
                    "toDayOfWeek": 6,
                    "fromHour": end_dt.hour,
                    "fromMinute": end_dt.minute,
                    "toHour": 23,
                    "toMinute": 30
                }
            ]
        }

    tarriffname = strftime("Go %Y%m%d %H%M%S", gmtime())
    logger.info("Tariff name: %s", tarriffname)

    sample_json = {
   "tou_settings":{
      "tariff_content":{
         "daily_charges":[
            {
               "name":"Charge",
               "amount":0
            }
         ],
         "demand_charges":{
            "ALL":{
               "ALL":0
            },
            "Summer":{

            },
            "Winter":{

            }
         },
         "utility":"Octopus",
         "energy_charges":{
            "ALL":{
               "ALL":0
            },
            "Summer":{
                "OFF_PEAK": 0.08,
                "ON_PEAK": 0.3
            },
            "Winter":{

            }
         },
         "name":tarriffname,
         "seasons":{
            "Summer":{
               "fromMonth":1,
               "fromDay":1,
               "toDay":31,
               "toMonth":12,
                "tou_periods": {}
            },
            "Winter":{
               "tou_periods":{

               }
            }
         },
         "sell_tariff":{
            "daily_charges":[
               {
                  "name":"Charge",
                  "amount":0
               }
            ],
            "demand_charges":{
               "ALL":{
                  "ALL":0
               },
               "Summer":{

               },
               "Winter":{

               }
            },
            "utility":"Octopus",
            "energy_charges":{
               "ALL":{
                  "ALL":0
               },
               "Summer":{
                    "OFF_PEAK": 0,
                    "ON_PEAK": 0
               },
               "Winter":{

               }
            },
            "name":tarriffname,
            "seasons":{
               "Summer":{
                  "fromMonth":1,
                  "fromDay":1,
                  "toDay":31,
                  "toMonth":12,
                  "tou_periods": {}
               },
               "Winter":{
                  "tou_periods":{

                  }
               }
            }
         }
      }
   }
}

    sample_json["tou_settings"]["tariff_content"]["seasons"]["Summer"]["tou_periods"].update(output_json)
    sample_json["tou_settings"]["tariff_content"]["sell_tariff"]["seasons"]["Summer"]["tou_periods"].update(output_json)

    # Display the converted JSON

    return sample_json


def send_tou_settings(json_data):
    logger.info("Sending TOU settings to Tesla API")

    import requests

    # Read the content from the original file.
    # cli.py -l outputs one "Product N:" block per product,
    # each block is a Python dict repr (not valid JSON) spanning multiple lines.
    # Use a regex to find energy_site_id directly — more robust than
    # parsing Python dict reprs with ast.literal_eval.
    import re

    with open('sites.json', 'r') as file:
        data = file.read()

    match = re.search(r'"energy_site_id"\s*:\s*(\d+)', data)
    if match:
        mysite = int(match.group(1))
    else:
        print("No energy site found in cli.py output")
        return

    print(mysite)

    "first string is: %s, second one is: %s"
    # API endpoint and JSON data
    api_url = "https://owner-api.teslamotors.com/api/1/energy_sites/%s/time_of_use_settings"  % (mysite)

    with open('cache.json') as f:
        cachejson = json.load(f)

    access_token = cachejson[myemail]["sso"]["access_token"]

    #print (access_token)

    # Step 2: Make a POST request to the API with the Bearer token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "User-Agent": "TeslaApp/4.8.0-1025/3e45238df4/android/11",
        "X-Tesla-User-Agent": "TeslaApp/4.8.0-1025/3e45238df4/android/11"
    }
    print(headers)
    print(json_data)
    api_response = requests.post(api_url, json=json_data, headers=headers)

    # Check the API response
    if api_response.status_code == 200:
        logger.info("API request successful: %s", api_response.json())
        print("API request successful!")
        print(api_response.json())
    else:
        logger.error("API request failed with status code %d: %s", api_response.status_code, api_response.text)
        print(f"API request failed with status code {api_response.status_code}: {api_response.text}")



def loadjsonfiles():
    import os

    # Read refresh token from cache and pass it to cli.py to force refresh
    with open('cache.json') as f:
        cachejson = json.load(f)

    refresh_token = cachejson[myemail]["sso"]["refresh_token"]
    os.system("python cli.py -e '%s' -l -R '%s' > sites.json" % (myemail, refresh_token))
    os.system("python io.py > latest.json")


def load_latest_json():
    try:
        with open('latest.json') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_current_next_run_start():
    latest = load_latest_json()
    if latest and 'nextRunStart' in latest:
        return latest['nextRunStart']
    return None


def run_pipeline(input_startDt=None, input_endDt=None):
    logger.info("Starting run pipeline")

    current_start = get_current_next_run_start()

    if input_startDt is not None:
        incoming_start = input_startDt
    else:
        try:
            with open('latest.json') as f:
                iojson = json.load(f)
            incoming_start = iojson.get('nextRunStart')
        except FileNotFoundError:
            incoming_start = None

    logger.info("Incoming startDt: %s, Current latest.json nextRunStart: %s", incoming_start, current_start)

    if incoming_start == current_start:
        logger.info("Incoming startDt matches latest.json, skipping Octopus API call")
        return JSONResponse(content={
            "status": "skipped",
            "reason": "no_change",
            "message": "No changes detected. Latest startDt matches latest.json.",
            "nextRunStart": current_start
        })

    logger.info("Calling Octopus API via io.py...")
    os.system("python io.py > latest.json")

    new_latest = load_latest_json()
    new_start = new_latest.get('nextRunStart') if new_latest else None

    if new_start == current_start:
        logger.info("Octopus result unchanged, skipping Tesla API call")
        return JSONResponse(content={
            "status": "skipped",
            "reason": "octopus_unchanged",
            "message": "Octopus API returned the same data. Tesla API not called.",
            "nextRunStart": new_start
        })

    logger.info("Octopus data changed, proceeding to Tesla API...")

    if input_startDt and input_endDt:
        times_obj = [{"startDt": input_startDt, "endDt": input_endDt}]
        json_input = json.dumps(times_obj)
        outputjson = tou_json(json_input)
    else:
        timesObj_val = new_latest.get("timesObj")
        timesObj = json.dumps(timesObj_val, indent=4)
        outputjson = tou_json(timesObj)

    print(json.dumps(outputjson, indent=4))
    send_tou_settings(outputjson)

    return JSONResponse(content={
        "status": "complete",
        "message": "TOU settings generated and sent to Tesla API.",
        "nextRunStart": new_start
    })


@asynccontextmanager
async def lifespan(app):
    logger.info("TeslaPy API server starting up")
    yield
    logger.info("TeslaPy API server shutting down")


# --- API layer ---
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional


class TimesObjInput(BaseModel):
    startDt: str
    endDt: str
    device_type: Optional[str] = None


app = FastAPI(title="TeslaPy API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/status")
async def get_status():
    """Returns the current script configuration."""
    return {
        "myemail": myemail,
        "functions": [
            "tou_json(input_json) -> dict",
            "send_tou_settings(json_data) -> None",
            "loadjsonfiles() -> None",
            "run_pipeline(input_startDt, input_endDt) -> JSONResponse",
        ]
    }


@app.post("/api/tou-json")
async def api_tou_json(input: TimesObjInput):
    """Convert startDt/endDt to a TOU JSON payload (does not send to Tesla)."""
    try:
        times_obj = [{"startDt": input.startDt, "endDt": input.endDt}]
        json_input = json.dumps(times_obj)
        result = tou_json(json_input)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error("Error in tou_json: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/run")
async def api_run(input: TimesObjInput | None = None):
    """Full pipeline: compare to latest.json, call Octopus API if needed,
    then call Tesla API if data changed.
    """
    try:
        if input is not None:
            return run_pipeline(input.startDt, input.endDt)
        else:
            return run_pipeline()
    except Exception as e:
        logger.error("Error in run pipeline: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/send")
async def api_send_tou(payload: dict):
    """Send an already-formed TOU JSON payload to Tesla.

    The caller must supply the same structure that ``tou_json`` returns.
    """
    try:
        send_tou_settings(payload)
        return JSONResponse(content={
            "status": "complete",
            "message": "TOU settings sent to Tesla API."
        })
    except Exception as e:
        logger.error("Error in send_tou_settings: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import sys
    import uvicorn

    # If run as a script without arguments, keep the old CLI behaviour
    if len(sys.argv) == 1:
        logger.info("=== Starting iotesla run ===")

        loadjsonfiles()

        with open('latest.json') as f:
            iojson = json.load(f)

        timesObj_val = iojson["timesObj"]
        timesObj = json.dumps(timesObj_val, indent=4)

        input_data = json.loads(timesObj)
        outputjson = tou_json(timesObj)

        print(json.dumps(outputjson, indent=4))

        send_tou_settings(outputjson)

        logger.info("=== iotesla run complete ===")
    else:
        # uvicorn --host 0.0.0.0 --port 8000 iotesla:app
        host = "0.0.0.0"
        port = 8080
        for i in range(0, len(sys.argv) - 1, 2):
            arg = sys.argv[i + 1]
            if arg in ("-p", "--port") and i + 2 < len(sys.argv):
                port = int(sys.argv[i + 2])
            elif arg in ("-h", "--host") and i + 2 < len(sys.argv):
                host = sys.argv[i + 2]
        uvicorn.run(app, host=host, port=port)
