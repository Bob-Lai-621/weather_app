# AI Prompt: Write a Python function to fetch weather data from OpenWeather API.

import requests
from datetime import datetime

def get_weather(city):
    # You'll need to sign up for a free API key at openweathermap.org
    API_KEY = "0e4ddcaaea96bb9e2f96d9c874c7ffab"  
    
    # Get current weather
    current_url = "http://api.openweathermap.org/data/2.5/weather"
    forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"  # For Celsius
    }
    
    try:
        # Get current weather
        current_response = requests.get(current_url, params=params)
        current_response.raise_for_status()  # Raises an HTTPError for bad responses
        current = current_response.json()
        
        # Get forecast
        forecast_response = requests.get(forecast_url, params=params)
        forecast_response.raise_for_status()
        forecast = forecast_response.json()
        
        # Current weather
        current_temp = current["main"]["temp"]
        current_desc = current["weather"][0]["description"]
        
        # Tomorrow's forecast (index 8 gives us data for 24 hours from now)
        tomorrow = forecast["list"][8]
        tomorrow_temp = tomorrow["main"]["temp"]
        tomorrow_desc = tomorrow["weather"][0]["description"]
        tomorrow_time = datetime.fromtimestamp(tomorrow["dt"]).strftime('%Y-%m-%d %H:%M')
        
        return (f"Current: {current_temp}°C, {current_desc}\n"
                f"Tomorrow ({tomorrow_time}): {tomorrow_temp}°C, {tomorrow_desc}")
                
    except requests.RequestException as e:
        return f"Network error: {str(e)}"
    except KeyError as e:
        return f"Error parsing weather data: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# Example usage
print(get_weather("London"))
