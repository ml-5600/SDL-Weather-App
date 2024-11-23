import json
from opencage.geocoder import OpenCageGeocode
import requests
import sdl2
import sdl2.ext

class Forecast:
    def __init__(self):
        pass

    def get_zip_code():
        print("Enter a 5-digit ZIP code:")
        zip_code = input()
        while not (len(zip_code) == 5 and zip_code.isdigit()):
            print("Enter a 5-digit US ZIP code:")
            zip_code = input()
        return zip_code

    def get_forecast(self):
        key = "cb8e807defef46ceb86f16b64365577b"
        geocoder = OpenCageGeocode(key)
        query = Forecast.get_zip_code()
        
        # Forward geocode the ZIP code to retrieve coordinates
        results = geocoder.geocode(query, no_annotations=1, countrycode='us')
        latitude = results[0]["geometry"]["lat"]
        longitude = results[0]["geometry"]["lng"]

        url = f"https://api.weather.gov/points/{latitude},{longitude}"
        response = requests.get(url)
        
        if response.status_code == 200:
            forecast_data = response.json()
            forecast_url = forecast_data['properties']['forecast']
            forecast_response = requests.get(forecast_url)

        if forecast_response.status_code == 200:
            forecast = forecast_response.json()
            return forecast

    def display_forecast(self, forecast):
        pass

def main():
    forecast = Forecast()
    forecast.display_forecast(forecast.get_forecast())

if __name__ == "__main__" :
    main()
