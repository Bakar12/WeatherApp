import requests

API_KEY = 'f3f6e6e8bc0e048b8fafcdd9be6d677b'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'


def get_weather(location):
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'metric'  # Use 'imperial' for Fahrenheit
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def display_weather(data):
    if data:
        main = data['main']
        weather = data['weather'][0]
        wind = data['wind']

        print(f"Weather for {data['name']}, {data['sys']['country']}:")
        print(f"Description: {weather['description'].capitalize()}")
        print(f"Temperature: {main['temp']}°C")
        print(f"Humidity: {main['humidity']}%")
        print(f"Wind Speed: {wind['speed']} m/s")
    else:
        print("Error fetching weather data.")


if __name__ == "__main__":
    location = input("Enter the location: ")
    weather_data = get_weather(location)
    display_weather(weather_data)

