import os
import requests
from datetime import datetime
from flask import Flask, render_template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Home Assistant configuration
HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "YOUR_LONG_LIVED_ACCESS_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json"
}

# Sensor entity IDs
TEMP_SENSOR_ID = "sensor.0x00124b0023c38740_temperature"
HUMIDITY_SENSOR_ID = "sensor.0x00124b0023c38740_humidity"

# Add Jinja2 template filters
@app.template_filter('datetime')
def format_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    if value is None:
        return ""
    return datetime.now().strftime(format)

@app.template_filter('to_float')
def to_float(value, default=0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def get_sensor_data(entity_id):
    """Fetch sensor data from Home Assistant"""
    try:
        url = f"{HA_URL}/api/states/{entity_id}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "state": data.get("state", "N/A"),
            "unit": data.get("attributes", {}).get("unit_of_measurement", "")
        }
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching {entity_id}: {e}")
        return {
            "state": "N/A",
            "unit": ""
        }

@app.route('/')
def index():
    # Get temperature data
    temp_data = get_sensor_data(TEMP_SENSOR_ID)
    temp_value = temp_data["state"]
    temp_unit = temp_data["unit"]
    
    # Get humidity data
    humidity_data = get_sensor_data(HUMIDITY_SENSOR_ID)
    humidity_value = humidity_data["state"]
    humidity_unit = humidity_data["unit"]
    
    # Set status message based on temperature
    status_message = "Chill factor optimal."
    try:
        if temp_value != "N/A" and float(temp_value) > 6:
            status_message = "Warning: Chill factor compromised."
    except (ValueError, TypeError):
        # If we can't convert temperature to float, keep default message
        pass
    
    return render_template('index.html', 
                          temp_value=temp_value,
                          temp_unit=temp_unit,
                          humidity_value=humidity_value,
                          humidity_unit=humidity_unit,
                          status_message=status_message)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 