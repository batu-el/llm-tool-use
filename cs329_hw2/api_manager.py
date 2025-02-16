import os
import requests
from datetime import datetime
from openai import OpenAI
import json
from googleapiclient.discovery import build
from textblob import TextBlob
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
import pytz

class APIManager:
    """A unified class to manage various API interactions"""
    
    def __init__(self, google_api_key: str, google_cx_id: str, alpha_vantage_key: str):
        """
        INPUT:
            google_api_key: str - Google API key for Custom Search
            google_cx_id: str - Google Custom Search Engine ID
            alpha_vantage_key: str - Alpha Vantage API key
            
        Initializes API keys and configurations
        """
        ################ CODE STARTS HERE ###############
        # Google
        self.google_api_key = google_api_key
        self.google_cx_id = google_cx_id
        # Finance
        self.alpha_vantage_url = "https://www.alphavantage.co/query"
        self.alpha_vantage_key = alpha_vantage_key
        # Weather
        self.geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"
        ################ CODE ENDS HERE ###############

    def parse_query_params(self, query: str, function_name: str) -> Optional[Dict]:
        """
        INPUT:
            query: str - Natural language query from user
            function_name: str - Name of the function to parse parameters for
            
        OUTPUT:
            Optional[Dict] - Parameters needed for the specified function or None if parsing fails
        """
        ################ CODE STARTS HERE ###############

        pass

        ################ CODE ENDS HERE ###############

    def route_query(self, query: str) -> Dict:
        """
        INPUT:
            query: str - Natural language query to route
            
        OUTPUT:
            Dict containing:
                - results: Any - Results from the API call
                - api_used: str - Name of the API that was used
                - error: str (optional) - Error message if something went wrong
        """
        ################ CODE STARTS HERE ###############
        route_query
        pass

        ################ CODE ENDS HERE ###############
        
    def google_search(self, search_term: str, num_results: int = 10) -> List[Dict]:
        """
        INPUT:
            search_term: str - The search query
            num_results: int - Number of results to return (default: 10)
            
        OUTPUT:
            List[Dict] - List of search results, each containing:
                - title: str
                - link: str
                - snippet: str
                - webpage_content: Dict (optional)
        """
        ################ CODE STARTS HERE ############### 
        service = build("customsearch", "v1", developerKey=self.google_api_key)
        res = service.cse().list(q=search_term, cx=self.google_cx_id, num=num_results).execute()
        items = res["items"]
        results = [{"title":item.get("title"),"link":item.get("link"),"snippet": item.get("snippet")} for item in items]
        ### Webpage Content ###
        max_length = 400
        for idx, result in enumerate(results):
            response = requests.get(result["link"], timeout=5)
            try:
                assert response.status_code == 200
                soup = BeautifulSoup(response.text, "html.parser")
                webpage_content = soup.get_text(separator=" ", strip=True)
                results[idx]["webpage_content"] = webpage_content[:max_length] + "..." if len(webpage_content) > max_length else webpage_content
            except:
                results[idx]["webpage_content"] = [{"ERROR": f"Error Status: {response.status_code}"}]
        return results
        ################ CODE ENDS HERE ###############
    
    def get_stock_data(self, symbol: str, date: Optional[str] = None) -> Dict:
        """
        INPUT:
            symbol: str - Stock symbol (e.g., 'AAPL')
            date: Optional[str] - Date in format 'YYYY-MM-DD'
            
        OUTPUT:
            Dict containing either:
                Current data:
                    - symbol: str
                    - price: float
                    - change: float
                    - change_percent: str
                Historical data:
                    - date: str
                    - open: float
                    - high: float
                    - low: float
                    - close: float
                    - volume: int
        """
        ################ CODE STARTS HERE ###############
        def current_data_f():
            params = {"function": "GLOBAL_QUOTE","symbol": symbol,"apikey": self.alpha_vantage_key}
            response = requests.get(self.alpha_vantage_url, params=params)
            data = response.json() 
            quote = data.get("Global Quote", {})  
            if quote:
                return {"symbol": quote["01. symbol"],"price": float(quote["05. price"]),"change": float(quote["09. change"]),"change_percent": quote["10. change percent"]}
            return
        def historical_data_f():
            params = {"function": "TIME_SERIES_DAILY","symbol": symbol,"apikey": self.alpha_vantage_key,"outputsize": "compact"}
            response = requests.get(self.alpha_vantage_url, params=params)
            data = response.json()     
            time_series = data.get("Time Series (Daily)", {})
            if date in time_series:
                stock_info = time_series[date]
                return {"date": date,"open": float(stock_info["1. open"]), "high": float(stock_info["2. high"]), "low": float(stock_info["3. low"]), "close": float(stock_info["4. close"]), "volume": int(stock_info["5. volume"])}
        return historical_data_f() if date else current_data_f()
        ################ CODE ENDS HERE ###############
    
    @staticmethod
    def analyze_sentiment(text: str) -> Dict:
        """
        INPUT:
            text: str - Text to analyze
            
        OUTPUT:
            Dict containing:
                - sentiment: str - "positive", "negative", or "neutral"
                - polarity: float - Sentiment polarity score
                - subjectivity: float - Subjectivity score
        """
        ################ CODE STARTS HERE ###############
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity
        sentiment = "neutral"
        if polarity > 0.1:
            sentiment = "positive"
        if polarity < -0.1:
            sentiment = "negative"
        return {"sentiment": sentiment,"polarity": polarity,"subjectivity": subjectivity}
        ################ CODE ENDS HERE ###############
    
    @staticmethod
    def get_weather(location: str, date: str, hour: str = "12") -> Dict:
        """
        INPUT:
            location: str - Location string (e.g., "Palo Alto, CA")
            date: str - Date in YYYY-MM-DD format
            hour: str - Hour in 24-hour format (default: "12")
            
        OUTPUT:
            Dict containing:
                - temperature: str
                - weather_description: str
                - humidity: str
                - wind_speed: str, any wind speed value is acceptable
        """
        ################ CODE STARTS HERE ###############
        ### Input Parameters ###        
        geocode = APIManager._get_coordinates(location.split(",")[0]) # only takes the city as input (can add the state with admin1 parameter)
        try:
            params = {"latitude": geocode["latitude"],"longitude": geocode["longitude"], "hourly": ["temperature_2m", "relative_humidity_2m", "windspeed_10m", "weathercode"],"timezone": "auto","start_date": date,"end_date": date}
        except:
            return {"ERROR": f"geocode output - {geocode}"}
        ### API Request ###
        forecast_url = "https://api.open-meteo.com/v1/forecast"
        response = requests.get(forecast_url, params=params)
        try:
            assert response.status_code == 200
            hour_index = int(hour) 
            data = response.json()['hourly']
            temperature = data['temperature_2m'][hour_index]
            humidity = data['relative_humidity_2m'][hour_index]
            wind_speed = data['windspeed_10m'][hour_index]
            weather_code = data['weathercode'][hour_index]
        except:
            return {"ERROR": f"Error Status: {response.status_code}"}
        ### Weather Description ###
        weather_description = APIManager._get_weather_description(weather_code)
        ### Final Output ###
        return {"temperature": f"{temperature}", "weather_description": weather_description,"humidity": f"{humidity}","wind_speed": f"{wind_speed} km/h"}
        ################ CODE ENDS HERE ###############
    
    @staticmethod
    def _get_coordinates(location: str) -> Optional[tuple]:
        """
        INPUT:
            location: str - Location name to geocode
            
        OUTPUT:
            Optional[tuple] - (latitude: float, longitude: float) or None if not found
        """
        ################ CODE STARTS HERE ###############
        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": location,  "count": 1,   "language": "en", "format": "json"}
        response = requests.get(geocode_url, params=params)
        try:
            assert response.status_code == 200
            data = response.json()
            return {"latitude": data["results"][0]["latitude"],"longitude": data["results"][0]["longitude"]}
        except:
            return {"Error": f"Error Status: {response.status_code}"}
        ################ CODE ENDS HERE ###############
    
    @staticmethod
    def _get_weather_description(code: int) -> str:
        """
        INPUT:
            code: int - Weather condition code
            
        OUTPUT:
            str - Human-readable weather description
        """
        ################ CODE STARTS HERE ###############
        weather_descriptions = {"0": "Clear sky",
                                "1": "Mainly clear",
                                "2": "Partly cloudy",
                                "3": "Overcast",
                                "45": "Fog",
                                "48": "Depositing rime fog",
                                "51": "Light drizzle",
                                "53": "Moderate drizzle",
                                "55": "Dense drizzle",
                                "56": "Light freezing drizzle",
                                "57": "Dense freezing drizzle",
                                "61": "Slight rain",
                                "63": "Moderate rain",
                                "65": "Heavy rain",
                                "66": "Light freezing rain",
                                "67": "Heavy freezing rain",
                                "71": "Slight snowfall",
                                "73": "Moderate snowfall",
                                "75": "Heavy snowfall",
                                "77": "Snow grains",
                                "80": "Slight rain showers",
                                "81": "Moderate rain showers",
                                "82": "Violent rain showers",
                                "85": "Slight snow showers",
                                "86": "Heavy snow showers",
                                "95": "Slight or moderate thunderstorm",
                                "96": "Thunderstorm with slight hail",
                                "99": "Thunderstorm with heavy hail"
                                }
        weather_description = weather_descriptions.get(str(code), "Unknown")
        return weather_description
        ################ CODE ENDS HERE ###############