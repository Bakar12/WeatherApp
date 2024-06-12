# Weather Application

This is a simple Python application that fetches and displays weather data for a given location. The application uses the OpenWeatherMap API to fetch the data and caches it locally for 30 minutes to reduce unnecessary API calls.

## Requirements

- Python 3.6 or higher
- `requests` library

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
