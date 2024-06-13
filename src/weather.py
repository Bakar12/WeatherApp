import requests
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import StringVar
from tkinter.ttk import Combobox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import geocoder

# Load configuration from a JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

API_KEY = config['api_key']
BASE_URL = 'http://api.openweathermap.org/data/2.5/'
CACHE_FILE = 'weather_cache.json'
CACHE_EXPIRY = timedelta(minutes=30)  # Cache expiry time


def load_cache():
    """Load the cache from the cache file if it exists."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            return json.load(file)
    return {}


def save_cache(cache):
    """Save the cache to the cache file."""
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file)


def get_weather(location, units='metric'):
    """Fetch weather data for a given location and units."""
    if not location:
        messagebox.showerror("Error", "Location cannot be empty.")
        return None

    # Load cache
    cache = load_cache()

    # Check if the location is in the cache and not expired
    if location in cache:
        timestamp, data = cache[location]
        if datetime.now() - datetime.fromisoformat(timestamp) < CACHE_EXPIRY:
            return data

    # Make the API request
    params = {
        'q': location,
        'appid': API_KEY,
        'units': units
    }
    try:
        response = requests.get(BASE_URL + 'weather', params=params)
        response.raise_for_status()
        data = response.json()

        # Handle case where city is not found
        if data.get('cod') != 200:
            messagebox.showerror("Error", data.get('message', 'Unknown error'))
            return None

        # Save to cache
        cache[location] = (datetime.now().isoformat(), data)
        save_cache(cache)
        return data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Network error: {e}")
        return None


def get_forecast(location, units='metric'):
    """Fetch 5-day weather forecast data for a given location and units."""
    params = {
        'q': location,
        'appid': API_KEY,
        'units': units
    }
    try:
        response = requests.get(BASE_URL + 'forecast', params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Network error: {e}")
        return None


def display_weather(data, units='metric'):
    """Format and return the weather data as a string."""
    if data:
        main = data['main']
        weather = data['weather'][0]
        wind = data['wind']
        sys = data['sys']
        unit_symbol = '°C' if units == 'metric' else '°F'
        speed_unit = 'm/s' if units == 'metric' else 'mph'

        result = (
            f"Weather for {data['name']}, {sys['country']}:\n"
            f"Description: {weather['description'].capitalize()}\n"
            f"Temperature: {main['temp']}{unit_symbol}\n"
            f"Humidity: {main['humidity']}%\n"
            f"Pressure: {main['pressure']} hPa\n"
            f"Visibility: {data.get('visibility', 'N/A')} meters\n"
            f"Wind Speed: {wind['speed']} {speed_unit}\n"
            f"Sunrise: {datetime.utcfromtimestamp(sys['sunrise']).strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Sunset: {datetime.utcfromtimestamp(sys['sunset']).strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        return result
    else:
        return "Error fetching weather data."


def fetch_weather():
    """Fetch and display the weather data based on user input."""
    location = location_var.get()
    units = unit_var.get()
    loading_label.config(text="Loading...")
    root.update_idletasks()
    weather_data = get_weather(location, units)
    loading_label.config(text="")
    result = display_weather(weather_data, units)
    result_label.config(text=result)
    if weather_data:
        icon_code = weather_data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        weather_icon_label.config(image='')
        weather_icon_label.image = tk.PhotoImage(file='')
        weather_icon_label.config(image=tk.PhotoImage(data=requests.get(icon_url).content))
        weather_icon_label.image = tk.PhotoImage(data=requests.get(icon_url).content)

        # Fetch and display forecast
        forecast_data = get_forecast(location, units)
        display_forecast(forecast_data)


def display_forecast(forecast_data):
    """Display a 5-day weather forecast."""
    if forecast_data:
        dates = []
        temps = []
        for entry in forecast_data['list']:
            date = datetime.utcfromtimestamp(entry['dt']).strftime('%Y-%m-%d %H:%M:%S')
            temp = entry['main']['temp']
            dates.append(date)
            temps.append(temp)

        fig, ax = plt.subplots()
        ax.plot(dates, temps, marker='o')
        ax.set_title('5-Day Weather Forecast')
        ax.set_xlabel('Date')
        ax.set_ylabel('Temperature (°C)')
        ax.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=6, column=0, columnspan=2)


def detect_location():
    """Detect the user's current location using geocoder."""
    g = geocoder.ip('me')
    if g.ok:
        location_var.set(g.city)
    else:
        messagebox.showerror("Error", "Unable to detect location.")


def switch_theme():
    """Switch between light and dark themes."""
    if root.tk.call("ttk::style", "theme", "use") == "clam":
        root.tk.call("ttk::style", "theme", "use", "alt")
    else:
        root.tk.call("ttk::style", "theme", "use", "clam")


# GUI setup
root = tk.Tk()
root.title("Weather App")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Label for location entry
location_label = ttk.Label(frame, text="Enter the location:")
location_label.grid(row=0, column=0, sticky=tk.W)

# Entry for location input
location_var = StringVar()
location_entry = ttk.Entry(frame, textvariable=location_var, width=50)
location_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

# Button to detect location
detect_button = ttk.Button(frame, text="Detect Location", command=detect_location)
detect_button.grid(row=0, column=2)

# Radio buttons for unit selection
unit_var = tk.StringVar(value='metric')
metric_rb = ttk.Radiobutton(frame, text="Metric", variable=unit_var, value='metric')
imperial_rb = ttk.Radiobutton(frame, text="Imperial", variable=unit_var, value='imperial')

metric_rb.grid(row=1, column=0, sticky=tk.W)
imperial_rb.grid(row=1, column=1, sticky=tk.W)

# Button to fetch weather data
fetch_button = ttk.Button(frame, text="Fetch Weather", command=fetch_weather)
fetch_button.grid(row=2, column=0, columnspan=2)

# Label to display weather results
result_label = ttk.Label(frame, text="", justify=tk.LEFT)
result_label.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

# Loading indicator label
loading_label = ttk.Label(frame, text="")
loading_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))

# Label to display weather icon
weather_icon_label = ttk.Label(frame, text="")
weather_icon_label.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))

# Button to switch themes
theme_button = ttk.Button(frame, text="Switch Theme", command=switch_theme)
theme_button.grid(row=5, column=2)

root.mainloop()
