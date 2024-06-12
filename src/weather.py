import requests
import json
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

API_KEY = config['api_key']
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
CACHE_FILE = 'weather_cache.json'
CACHE_EXPIRY = timedelta(minutes=30)  # Cache expiry time

def get_weather(location, units='metric'):
    # Load cache if available
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            cache = json.load(file)
            if location in cache:
                timestamp, data = cache[location]
                if datetime.now() - datetime.fromisoformat(timestamp) < CACHE_EXPIRY:
                    return data

    params = {
        'q': location,
        'appid': API_KEY,
        'units': units
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        # Save to cache
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as file:
                cache = json.load(file)
        else:
            cache = {}
        cache[location] = (datetime.now().isoformat(), data)
        with open(CACHE_FILE, 'w') as file:
            json.dump(cache, file)
        return data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Network error: {e}")
        return None

def display_weather(data, units='metric'):
    if data:
        main = data['main']
        weather = data['weather'][0]
        wind = data['wind']
        unit_symbol = '°C' if units == 'metric' else '°F'
        speed_unit = 'm/s' if units == 'metric' else 'mph'

        result = (
            f"Weather for {data['name']}, {data['sys']['country']}:\n"
            f"Description: {weather['description'].capitalize()}\n"
            f"Temperature: {main['temp']}{unit_symbol}\n"
            f"Humidity: {main['humidity']}%\n"
            f"Wind Speed: {wind['speed']} {speed_unit}\n"
        )
        return result
    else:
        return "Error fetching weather data."

def fetch_weather():
    location = location_entry.get()
    units = unit_var.get()
    weather_data = get_weather(location, units)
    result = display_weather(weather_data, units)
    result_label.config(text=result)

# GUI setup
root = tk.Tk()
root.title("Weather App")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

location_label = ttk.Label(frame, text="Enter the location:")
location_label.grid(row=0, column=0, sticky=tk.W)

location_entry = ttk.Entry(frame, width=50)
location_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

unit_var = tk.StringVar(value='metric')
metric_rb = ttk.Radiobutton(frame, text="Metric", variable=unit_var, value='metric')
imperial_rb = ttk.Radiobutton(frame, text="Imperial", variable=unit_var, value='imperial')

metric_rb.grid(row=1, column=0, sticky=tk.W)
imperial_rb.grid(row=1, column=1, sticky=tk.W)

fetch_button = ttk.Button(frame, text="Fetch Weather", command=fetch_weather)
fetch_button.grid(row=2, column=0, columnspan=2)

result_label = ttk.Label(frame, text="", justify=tk.LEFT)
result_label.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

root.mainloop()

