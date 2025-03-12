from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WeatherResponse(BaseModel):
    current_temp: float
    current_desc: str
    city: str
    forecast: Optional[dict] = None

@app.get("/api/weather/{city}")
async def get_weather(city: str, include_forecast: bool = False):
    API_KEY = "0e4ddcaaea96bb9e2f96d9c874c7ffab"
    
    try:
        # Get current weather
        current_url = "http://api.openweathermap.org/data/2.5/weather"
        forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"  # For Celsius
        }
        
        # Get current weather
        current_response = requests.get(current_url, params=params)
        current_response.raise_for_status()
        current = current_response.json()
        
        weather_data = {
            "current_temp": current["main"]["temp"],
            "current_desc": current["weather"][0]["description"],
            "city": current["name"]
        }
        
        if include_forecast:
            # Get forecast
            forecast_response = requests.get(forecast_url, params=params)
            forecast_response.raise_for_status()
            forecast = forecast_response.json()
            
            # Get next 5 days forecast
            forecast_data = []
            for i in range(8, 40, 8):  # Every 24 hours
                day = forecast["list"][i]
                forecast_data.append({
                    "temp": day["main"]["temp"],
                    "description": day["weather"][0]["description"],
                    "timestamp": day["dt"],
                    "date": datetime.fromtimestamp(day["dt"]).strftime('%Y-%m-%d')
                })
            
            weather_data["forecast"] = forecast_data
        
        return WeatherResponse(**weather_data)
                
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing weather data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Weather API is running. Use /api/weather/{city} to get weather data"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
