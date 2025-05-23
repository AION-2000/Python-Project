import requests
import pandas as pd
from datetime import datetime
import os  # Added os import to fix the error

# Replace with your valid OpenWeatherMap API key
API_KEY = "eb19f7e01a4063b289bf8ab54b59a57c"  # Replace with a valid key if this doesn't work
CITY = "Dhaka"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

try:
    # Fetch weather data
    response = requests.get(URL)
    response.raise_for_status()  # Raises an exception for 4xx/5xx errors

    # Parse JSON response
    try:
        data = response.json()
    except ValueError:
        print("❌ Error: Failed to parse API response as JSON")
        exit(1)

    # Check for required fields
    if not all(key in data for key in ["main", "weather"]):
        print("❌ Error: API response missing required fields (main or weather)")
        exit(1)

    # Extract weather data
    try:
        weather = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "city": CITY,
            "temperature": data["main"].get("temp", None),
            "humidity": data["main"].get("humidity", None),
            "pressure": data["main"].get("pressure", None),
            "weather": data["weather"][0].get("main", None) if data["weather"] else None
        }
    except (KeyError, IndexError) as e:
        print(f"❌ Error: Failed to extract data from API response: {e}")
        exit(1)

    # Save to CSV
    df = pd.DataFrame([weather])
    file_name = "weather_data.csv"

    try:
        # Append to existing CSV or create a new one
        if os.path.exists(file_name):
            df_existing = pd.read_csv(file_name)
            df = pd.concat([df_existing, df], ignore_index=True)
        df.to_csv(file_name, index=False)
        print("✅ Weather data saved successfully to weather_data.csv!")
    except (PermissionError, OSError) as e:
        print(f"❌ Error: Failed to save data to CSV: {e}")
        exit(1)

except requests.exceptions.RequestException as e:
    # Handle API request errors
    error_msg = "Unknown error"
    if response.status_code == 401:
        error_msg = "Invalid API key. Please get a valid key from https://openweathermap.org/"
    elif response.status_code == 404:
        error_msg = f"City '{CITY}' not found"
    elif response.status_code == 429:
        error_msg = "API rate limit exceeded"
    else:
        try:
            error_msg = response.json().get("message", "No error message provided")
        except Exception:
            error_msg = str(e)
    print(f"❌ Failed to fetch weather data: {error_msg} (Status code: {response.status_code})")