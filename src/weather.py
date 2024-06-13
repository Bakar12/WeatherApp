import os
import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import StringVar
from tkinter.ttk import Combobox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import geocoder
import gettext

# Set up localization with fallback
try:
    lang = gettext.translation('base', localedir='locales', languages=['es'])
    lang.install()
    _ = lang.gettext
except FileNotFoundError:
    # Fallback to default language (English)
    _ = lambda s: s

# Load configuration from a JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

API_KEY = config['api_key']
BASE_URL = 'http://api.openweathermap.org/data/2.5/'
HISTORICAL_BASE_URL = 'http://history.openweathermap.org/data/2.5/history/city'
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
        messagebox.showerror(_("Error"), _("Location cannot be empty."))
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
            messagebox.showerror(_("Error"), data.get('message', _('Unknown error')))
            return None

        # Save to cache
        cache[location] = (datetime.now().isoformat(), data)
        save_cache(cache)
        return data
    except requests.exceptions.RequestException as e:
        # If there's a network error, try to load from cache
        if location in cache:
            timestamp, data = cache[location]
            messagebox.showinfo(_("Offline Mode"), _("Loaded cached data due to network error."))
            return data
        else:
            messagebox.showerror(_("Error"), f"{_('Network error')}: {e}")
            return None

def get_weather_alerts(location):
    """Fetch weather alerts for a given location."""
    params = {
        'q': location,
        'appid': API_KEY,
    }
    try:
        response = requests.get(BASE_URL + 'alerts', params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        messagebox.showerror(_("Error"), f"{_('Network error')}: {e}")
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
        messagebox.showerror(_("Error"), f"{_('Network error')}: {e}")
        return None

def get_historical_weather(location, start, end, units='metric'):
    """Fetch historical weather data for a given location and date range."""
    params = {
        'q': location,
        'appid': API_KEY,
        'units': units,
        'type': 'hour',
        'start': int(start.timestamp()),
        'end': int(end.timestamp())
    }
    try:
        response = requests.get(HISTORICAL_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        messagebox.showerror(_("Error"), f"{_('Network error')}: {e}")
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
            f"{_('Weather for')} {data['name']}, {sys['country']}:\n"
            f"{_('Description')}: {weather['description'].capitalize()}\n"
            f"{_('Temperature')}: {main['temp']}{unit_symbol}\n"
            f"{_('Humidity')}: {main['humidity']}%\n"
            f"{_('Pressure')}: {main['pressure']} hPa\n"
            f"{_('Visibility')}: {data.get('visibility', 'N/A')} meters\n"
            f"{_('Wind Speed')}: {wind['speed']} {speed_unit}\n"
            f"{_('Sunrise')}: {datetime.utcfromtimestamp(sys['sunrise']).strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{_('Sunset')}: {datetime.utcfromtimestamp(sys['sunset']).strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        return result
    else:
        return _("Error fetching weather data.")

def display_weather_alerts(data):
    """Display weather alerts if any."""
    if data and 'alerts' in data:
        alerts = data['alerts']
        if alerts:
            alerts_text = _("Weather Alerts") + ":\n"
            for alert in alerts:
                alerts_text += f"- {alert['event']}: {alert['description']}\n"
            return alerts_text
    return _("No weather alerts.")

def fetch_weather():
    """Fetch and display the weather data based on user input."""
    location = location_var.get()
    units = unit_var.get()
    loading_label.config(text=_("Loading..."))
    root.update_idletasks()
    weather_data = get_weather(location, units)
    alerts_data = get_weather_alerts(location)
    loading_label.config(text="")
    result = display_weather(weather_data, units)
    result_label.config(text=result)
    alerts = display_weather_alerts(alerts_data)
    alerts_label.config(text=alerts)
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
        ax.set_title(_('5-Day Weather Forecast'))
        ax.set_xlabel(_('Date'))
        ax.set_ylabel(_('Temperature (°C)'))
        ax.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=9, column=0, columnspan=2)

def detect_location():
    """Detect the user's current location using geocoder."""
    g = geocoder.ip('me')
    if g.ok:
        location_var.set(g.city)
    else:
        messagebox.showerror(_("Error"), _("Unable to detect location."))

def switch_theme():
    """Switch between light and dark themes."""
    if root.tk.call("ttk::style", "theme", "use") == "clam":
        root.tk.call("ttk::style", "theme", "use", "alt")
    else:
        root.tk.call("ttk::style", "theme", "use", "clam")

def fetch_suggestions():
    """Fetch location suggestions from the API."""
    query = location_var.get()
    if len(query) > 2:
        params = {
            'q': query,
            'appid': API_KEY,
        }
        try:
            response = requests.get(BASE_URL + 'find', params=params)
            response.raise_for_status()
            data = response.json()
            suggestions = [item['name'] for item in data['list']]
            location_combobox['values'] = suggestions
        except requests.exceptions.RequestException as e:
            messagebox.showerror(_("Error"), f"{_('Network error')}: {e}")

def on_location_change(event):
    """Fetch suggestions when the location entry is modified."""
    fetch_suggestions()

def load_locations():
    """Load the saved locations from a file."""
    if os.path.exists('locations.json'):
        with open('locations.json', 'r') as file:
            return json.load(file)
    return []

def save_location(location):
    """Save a new location to the file."""
    locations = load_locations()
    if location not in locations:
        locations.append(location)
        with open('locations.json', 'w') as file:
            json.dump(locations, file)
        update_location_list()

def update_location_list():
    """Update the location list in the UI."""
    location_list = load_locations()
    location_combobox['values'] = location_list

def select_location(event):
    """Set the selected location from the combobox."""
    selected_location = location_combobox.get()
    location_var.set(selected_location)
    fetch_weather()

def fetch_historical_weather():
    """Fetch and display historical weather data based on user input."""
    location = location_var.get()
    start_date = start_date_var.get()
    end_date = end_date_var.get()
    if not location or not start_date or not end_date:
        messagebox.showerror(_("Error"), _("Location and dates cannot be empty."))
        return
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    historical_data = get_historical_weather(location, start, end)
    display_historical_weather(historical_data)

def display_historical_weather(data):
    """Display historical weather data."""
    if data:
        hist_weather = _("Historical Weather") + ":\n"
        for entry in data['list']:
            date = datetime.utcfromtimestamp(entry['dt']).strftime('%Y-%m-%d %H:%M:%S')
            temp = entry['main']['temp']
            hist_weather += f"{date}: {temp}°C\n"
        historical_label.config(text=hist_weather)
    else:
        historical_label.config(text=_("Error fetching historical data."))

# GUI setup
root = tk.Tk()
root.title(_("Weather App"))

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Label for location entry
location_label = ttk.Label(frame, text=_("Enter the location:"))
location_label.grid(row=0, column=0, sticky=tk.W)

# Entry for location input
location_var = StringVar()
location_entry = ttk.Entry(frame, textvariable=location_var, width=50)
location_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
location_entry.bind('<KeyRelease>', on_location_change)

# Button to detect location
detect_button = ttk.Button(frame, text=_("Detect Location"), command=detect_location)
detect_button.grid(row=0, column=2)

# Radio buttons for unit selection
unit_var = tk.StringVar(value='metric')
metric_rb = ttk.Radiobutton(frame, text=_("Metric"), variable=unit_var, value='metric')
imperial_rb = ttk.Radiobutton(frame, text=_("Imperial"), variable=unit_var, value='imperial')

metric_rb.grid(row=1, column=0, sticky=tk.W)
imperial_rb.grid(row=1, column=1, sticky=tk.W)

# Button to fetch weather data
fetch_button = ttk.Button(frame, text=_("Fetch Weather"), command=fetch_weather)
fetch_button.grid(row=2, column=0, columnspan=2)

# Button to save location
save_button = ttk.Button(frame, text=_("Save Location"), command=lambda: save_location(location_var.get()))
save_button.grid(row=2, column=2)

# Combobox to select saved locations
location_combobox = ttk.Combobox(frame)
location_combobox.grid(row=2, column=3)
location_combobox.bind("<<ComboboxSelected>>", select_location)
update_location_list()

# Label to display weather results
result_label = ttk.Label(frame, text="", justify=tk.LEFT)
result_label.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

# Label to display weather alerts
alerts_label = ttk.Label(frame, text="", justify=tk.LEFT)
alerts_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))

# Loading indicator label
loading_label = ttk.Label(frame, text="")
loading_label.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))

# Label to display weather icon
weather_icon_label = ttk.Label(frame, text="")
weather_icon_label.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))

# Start and end date inputs for historical weather
start_date_var = StringVar()
end_date_var = StringVar()

start_date_label = ttk.Label(frame, text=_("Start Date (YYYY-MM-DD):"))
start_date_label.grid(row=7, column=0, sticky=tk.W)

start_date_entry = ttk.Entry(frame, textvariable=start_date_var)
start_date_entry.grid(row=7, column=1, sticky=(tk.W, tk.E))

end_date_label = ttk.Label(frame, text=_("End Date (YYYY-MM-DD):"))
end_date_label.grid(row=8, column=0, sticky=tk.W)

end_date_entry = ttk.Entry(frame, textvariable=end_date_var)
end_date_entry.grid(row=8, column=1, sticky=(tk.W, tk.E))

historical_button = ttk.Button(frame, text=_("Fetch Historical Weather"), command=fetch_historical_weather)
historical_button.grid(row=9, column=0, columnspan=2)

historical_label = ttk.Label(frame, text="", justify=tk.LEFT)
historical_label.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E))

# Button to switch themes
theme_button = ttk.Button(frame, text=_("Switch Theme"), command=switch_theme)
theme_button.grid(row=10, column=2)

root.mainloop()
