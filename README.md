# Weather Application

This is a Python application that fetches and displays weather data for a given location. The application uses the OpenWeatherMap API to fetch the data and caches it locally for 30 minutes to reduce unnecessary API calls.

## Requirements

- Python 3.6 or higher
- `requests` library
- `tkinter` library
- `matplotlib` library
- `geocoder` library

## Features

- Fetches and displays current weather data for a given location.
- Provides auto-completion for city names.
- Displays an icon representing the current weather.
- Shows a 5-day weather forecast with a graph.
- Allows unit conversion through radio buttons for unit selection.
- Uses ttk widgets for better responsiveness.
- Includes a button to switch between light and dark themes.
- Displays weather icons from the API.
- Includes a graph for the 5-day forecast.
- Improved UI with better layout and custom buttons.
- Includes a button to detect the user's current location.

## Setup

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required Python libraries using pip:
    ```
    pip install -r requirements.txt
    ```
4. Run the application:
    ```
    python weather.py
    ```
5. Enter the name of a city or town when prompted.
6. The application will display the current weather data for the location.

## Usage

When you run the application, you will be prompted to enter a location and choose the unit of measurement (metric or imperial). The application will then fetch and display the weather data for the specified location.

## Caching

The application caches the weather data locally in a file named `weather_cache.json`. The cache expires after 30 minutes. If the cache for a location is not expired, the application will use the cached data instead of making a new API call.

## API Key

The application uses the OpenWeatherMap API to fetch weather data. You need to replace the `API_KEY` in the `src/weather.py` file with your own API key from OpenWeatherMap.

## License

This project is licensed under the MIT License.
