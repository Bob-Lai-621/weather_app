from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

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
    temperature: float
    description: str
    city: str
    forecast: Optional[dict] = None

@app.get("/weather/{city}", response_class=HTMLResponse)
async def get_weather(city: str, include_forecast: bool = False):
    API_KEY = "0e4ddcaaea96bb9e2f96d9c874c7ffab"
    
    try:
        # Get current weather
        current_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"  # For Celsius
        }
        
        response = requests.get(current_url, params=params)
        response.raise_for_status()
        current_data = response.json()
        
        weather_info = {
            "temperature": current_data["main"]["temp"],
            "description": current_data["weather"][0]["description"],
            "city": current_data["name"]
        }
        
        # Create HTML response
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Weather for {weather_info['city']}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f0f8ff;
                }}
                .weather-card {{
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .forecast-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }}
                .forecast-card {{
                    background-color: white;
                    border-radius: 10px;
                    padding: 15px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .temperature {{
                    font-size: 2em;
                    color: #0066cc;
                }}
                .description {{
                    color: #666;
                    text-transform: capitalize;
                }}
                .date {{
                    color: #333;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                h1 {{
                    color: #333;
                }}
            </style>
        </head>
        <body>
            <h1>Weather in {weather_info['city']}</h1>
            <div class="weather-card">
                <h2>Current Weather</h2>
                <div class="temperature">{weather_info['temperature']}°C</div>
                <div class="description">{weather_info['description']}</div>
            </div>
        """
        
        if include_forecast:
            # Get 5-day forecast
            forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
            forecast_response = requests.get(forecast_url, params=params)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            html_content += """
            <div class="weather-card">
                <h2>5-Day Forecast</h2>
                <div class="forecast-grid">
            """
            
            # Get one forecast per day (every 8th item is 24 hours apart)
            for i in range(8, 40, 8):
                day = forecast_data["list"][i]
                forecast_time = datetime.fromtimestamp(day["dt"])
                temp = day["main"]["temp"]
                desc = day["weather"][0]["description"]
                
                html_content += f"""
                <div class="forecast-card">
                    <div class="date">{forecast_time.strftime('%A, %b %d')}</div>
                    <div class="temperature">{temp}°C</div>
                    <div class="description">{desc}</div>
                </div>
                """
            
            html_content += """
                </div>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing weather data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f0f8ff;
            }
            .card {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            code {
                background-color: #f4f4f4;
                padding: 2px 5px;
                border-radius: 3px;
            }
            .example {
                color: #0066cc;
            }
        </style>
    </head>
    <body>
        <h1>Welcome to the Weather API!</h1>
        <div class="card">
            <h2>Usage</h2>
            <p><strong>Endpoint:</strong> <code>/weather/{city}</code></p>
            <h3>Parameters:</h3>
            <ul>
                <li><code>city</code>: Name of the city (required)</li>
                <li><code>include_forecast</code>: Set to true to include tomorrow's forecast (optional)</li>
            </ul>
            <h3>Example:</h3>
            <p class="example"><a href="/weather/london?include_forecast=true">/weather/london?include_forecast=true</a></p>
        </div>
        <div class="card">
            <h2>Status</h2>
            <p>✅ Service is running</p>
        </div>
    </body>
    </html>
    """
