import json
from opencage.geocoder import OpenCageGeocode
import requests
import sdl2
import sdl2.ext
import sdl2.sdlmixer
import sdl2.sdlttf
import time

class Forecast:
    def __init__(self):
        self.isClear = False
    
    def get_zip_code():
        print("Enter a 5-digit ZIP code:")
        zip_code = input()
        while not (len(zip_code) == 5 and zip_code.isdigit()):
            print("Enter a 5-digit United States ZIP code:")
            zip_code = input()
        return zip_code

    def get_forecast(self):
        key = "cb8e807defef46ceb86f16b64365577b"
        geocoder = OpenCageGeocode(key)
        query = Forecast.get_zip_code()
        
        # Forward geocode the ZIP code to retrieve coordinates
        results = geocoder.geocode(query, no_annotations = 1, countrycode = 'us')
        latitude = results[0]["geometry"]["lat"]
        longitude = results[0]["geometry"]["lng"]

        url = f"https://api.weather.gov/points/{latitude},{longitude}"
        response = requests.get(url)
        
        # Check if each response is valid
        if response.status_code == 200:
            forecast_data = response.json()
            forecast_url = forecast_data['properties']['forecast']
            forecast_response = requests.get(forecast_url)

        if forecast_response.status_code == 200:
            forecast = forecast_response.json()
            # Add the city and state to the forecast
            # Geocoder's location _type is not always "city"
            forecast["city"] = ( 
                results[0]["components"].get("city") or
                results[0]["components"].get("_normalized_city") or
                results[0]["components"].get("town") or
                results[0]["components"].get("village") or
                results[0]["components"].get("place") or
                results[0]["components"].get("postal_city") or
                results[0]["components"].get("hamlet") or
                results[0]["components"].get("region") or
                results[0]["components"].get("neighborhood") or
                results[0]["components"].get("suburb") or
                results[0]["components"].get("county") or
                "Unknown")
            forecast["state"] = results[0]["components"]["state"] 
            return forecast

    def get_weather_icon(self, forecast, factory, RESOURCES, font_path, color):
        # Check which weather icon should be loaded
        words_to_check = {"cloudy", "fog", "foggy", "overcast"}
        if any(word in (forecast["properties"]["periods"][0]["detailedForecast"]).lower() 
            for word in words_to_check):
            weather_icon = factory.from_image(RESOURCES.get_path("cloudy.png"))
            return weather_icon

        words_to_check = {"hail", "hailing"}
        if any(word in (forecast["properties"]["periods"][0]["detailedForecast"]).lower() 
            for word in words_to_check):
            weather_icon = factory.from_image(RESOURCES.get_path("hail.png"))
            return weather_icon

        words_to_check = {"sunny", "sunshine"}
        if any(word in (forecast["properties"]["periods"][0]["detailedForecast"]).lower() 
            for word in words_to_check):
            weather_icon = factory.from_image(RESOURCES.get_path("sunny.png"))
            return weather_icon
        
        words_to_check = {"showers", "rain", "raining"}
        if any(word in (forecast["properties"]["periods"][0]["detailedForecast"]).lower() 
            for word in words_to_check):
            weather_icon = factory.from_image(RESOURCES.get_path("showers.png"))
            return weather_icon
   
        words_to_check = {"snow", "snowy", "snowing"}
        if any(word in (forecast["properties"]["periods"][0]["detailedForecast"]).lower() 
            for word in words_to_check):
            weather_icon = factory.from_image(RESOURCES.get_path("snow.png"))
            return weather_icon

        words_to_check = {"thunderstorm", "thunder"}
        if any(word in (forecast["properties"]["periods"][0]["detailedForecast"]).lower() 
            for word in words_to_check):
            weather_icon = factory.from_image(RESOURCES.get_path("thunderstorm.png"))
            return weather_icon
        
        words_to_check = {"clear"}
        if any(word in (forecast["properties"]["periods"][0]["detailedForecast"]).lower() 
            for word in words_to_check):
            weather_icon = factory.from_text("Clear", fontmanager = sdl2.ext.FontManager(font_path, size = 100), color = color)
            self.isClear = True
            return weather_icon

        else:
            # None of the above; return a filler icon
            weather_icon = factory.from_color(color=(0, 0, 0, 0), size = (0, 0))
            return weather_icon

    def display_forecast(self, forecast):
        sdl2.ext.init()
        sdl2.sdlttf.TTF_Init()
        RESOURCES = sdl2.ext.Resources(__file__, "media")

        # Create the window  
        window = sdl2.ext.Window("Weather", size=(1024, 768))
        window.show()
        # Set a fixed frame rate
        FPS = 30
        frame_delay = 1.0 / FPS
        
        # Create a SpriteFactory and a SpriteRenderSystem
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        sprite_renderer = factory.create_sprite_render_system(window)

        # Create font managers and load resources
        font_path = RESOURCES.get_path("Roboto-Regular.ttf")     
        font_manager = sdl2.ext.FontManager(font_path, size = 50)
        font_manager_large = sdl2.ext.FontManager(font_path, size = 100)
     
        # Set day/night theme
        if (forecast["properties"]["periods"][0]["isDaytime"]):
            background_sprite = factory.from_image(RESOURCES.get_path("day.png"))                    
            color = (0, 0, 0)
            short_forecast = factory.from_text(forecast["properties"]["periods"][0]["shortForecast"], fontmanager = font_manager, color = (0, 0, 0))

        else:
            background_sprite = factory.from_image(RESOURCES.get_path("night.png"))
            color = (255, 255, 255)
            short_forecast = factory.from_text(forecast["properties"]["periods"][0]["shortForecast"], fontmanager = font_manager, color = (255, 255, 255))

        # Prepare sprites to be rendered
        weather_icon = self.get_weather_icon(forecast, factory, RESOURCES, font_path, color)
        window_width, window_height = window.size
        text_width, text_height = short_forecast.size
        x = (window_width - text_width) // 2
        y = (window_height - text_height) // 2

        current_temperature_text = str(forecast["properties"]["periods"][0]["temperature"])  + "°F"
        current_temperature_sprite = factory.from_text(current_temperature_text, 
            fontmanager = font_manager_large, color = color)
        
        precipitation_text = "Chance of precipitation: " + str(forecast["properties"]["periods"][0]["probabilityOfPrecipitation"]["value"])
        precipitation_sprite = factory.from_text(precipitation_text, 
            fontmanager = font_manager, color = color)

        wind_speed_text = "Wind speed: " + str(forecast["properties"]["periods"][0]["windSpeed"])
        wind_speed_sprite = factory.from_text(wind_speed_text, 
            fontmanager = font_manager, color = color)

        city_sprite = factory.from_text(forecast["city"] + ",", 
            fontmanager = font_manager, color = color)
        state_sprite = factory.from_text(forecast["state"], 
            fontmanager = font_manager, color = color)

        current_period = forecast["properties"]["periods"][0]["name"]
        current_period_sprite = factory.from_text(current_period, 
            fontmanager = font_manager, color = color)
        # Render the current weather conditions
        print(forecast["properties"]["periods"][0]["detailedForecast"])
        sprite_renderer.render(background_sprite)
        sprite_renderer.render(city_sprite, 20, y - 340)
        sprite_renderer.render(state_sprite, 20, y - 290)
        sprite_renderer.render(current_period_sprite, x, y - 340)
        sprite_renderer.render(current_temperature_sprite, x, y + 100)
        sprite_renderer.render(short_forecast, x, y + 210)
        sprite_renderer.render(precipitation_sprite, x // 2, y + 260)
        sprite_renderer.render(wind_speed_sprite, x // 2, y + 310)
        if (self.isClear):
            sprite_renderer.render(weather_icon, x, y - 120)
        else:
            sprite_renderer.render(weather_icon, x - 120, y - 370)

        # Play music file indefinitely
        sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 2048)
        audio_path = RESOURCES.get_path("music.mp3")
        music = sdl2.sdlmixer.Mix_LoadMUS(audio_path.encode("utf-8"))
        sdl2.sdlmixer.Mix_PlayMusic(music, -1)
                        
        #Event loop
        running = True
        while running:
            start_time = time.time()
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    # End the program
                    running = False
                    break
            window.refresh()

            # Cap the frame rate at 30 FPS
            elapsed_time = time.time() - start_time
            if (elapsed_time < frame_delay):
                time.sleep(frame_delay - elapsed_time)
        sdl2.ext.quit()

def main():
    forecast = Forecast()
    forecast.display_forecast(forecast.get_forecast())

if __name__ == "__main__" :
    main()