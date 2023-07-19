import json
import requests
from urllib.request import urlopen

# To Fetch location and coordinates
def location():
    url = 'http://ipinfo.io/json'
    response = urlopen(url)
    data = json.load(response)

    city = data['city']
    long, lat = data['loc'].split(',')
    return city, long, lat

# AccuWeatherAPI for LocationID
def LocationID(city):
    # query = city.lower()
    query = city

    # AccuWeatherAPI for LocationID
    ENDPOINT = "http://dataservice.accuweather.com/locations/v1/cities/search"
    api_key = "KAiKG8xfPKZqfu0mRiqTVg2imyNOZurR"

    IDParameters = {
        "apikey": api_key,
        "q": query,
    }

    AWResponse = requests.get(url=ENDPOINT, params=IDParameters)
    AWResponse.raise_for_status()

    return AWResponse.json()[0]["Key"]
    # print(f'{query} : {cityId}')
    # return cityId

# AccuWeatherAPI for Temperature and Rain
def tempRain(cityId):
    ENDPOINT = f'http://dataservice.accuweather.com/forecasts/v1/daily/1day/{cityId}'
    api_key = "KAiKG8xfPKZqfu0mRiqTVg2imyNOZurR"

    AWParameters = {
        "apikey": api_key,
        "details": True,
    }

    AWResponse = requests.get(url=ENDPOINT, params=AWParameters)
    AWResponse.raise_for_status()

    min_temperature = AWResponse.json()["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"]
    max_temperature = AWResponse.json()["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
    temp = (max_temperature + min_temperature) / 2
    temp = (temp - 32)/1.8
    rain = AWResponse.json()["DailyForecasts"][0]["Day"]["Rain"]["Value"] * 25.4
    # print(f'Temperature: {temp} C')
    # print(f'Rain: {rain} mm')
    return temp, rain


# OpenWeatherAPI for Humidity
def humidity(latitude, longitude):
    ENDPOINT = "https://api.openweathermap.org/data/2.5/onecall"
    api_key = "f6c1586d81afb95c234599cc660f643b"

    OWParameters = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
    }

    OWResponse = requests.get(url=ENDPOINT, params=OWParameters)
    OWResponse.raise_for_status()

    return OWResponse.json()["current"]["humidity"]
    # print(f'Humidity: {humidity} %')
    # return humidity

# city, long, lat = location()
# locationId = LocationID(city)
# temp, rain = tempRain(locationId)
# humid = humidity(lat, long)
# print([temp, rain, humid])