import pandas as pd
import math
import csv

def make_humidity(humidities):
    # print(set(humidities))
    humidities = [float(h) if h != ' ' else float('nan') for h in humidities]
    return [(h if not math.isnan(h) else 0, int(math.isnan(h))) for h in humidities]

def make_weather_detail(details):
    total = list(set(details))
    # print(total)
    weather_translations = {}
    for ind, weather in enumerate(total):
        weather_translations[weather] = [0] * len(total)
        weather_translations[weather][ind] = 1

    return weather_translations

def make_weather(weather_details, translations):
    return [translations[det] for det in weather_details]

def main():
    # teams = pd.read_csv('nfl_teams.csv')
    history = pd.read_csv('spreadspoke_scores.csv')
    history['schedule_date'] = pd.to_datetime(history['schedule_date'])
    history = history[(history['schedule_date'] < '2022-12-15')]
    # print(set(history['weather_humidity']), set(history['weather_detail']))
    # history
    history['weather_humidity'] = make_humidity(history['weather_humidity'])
    history['weather_wind_mph'] = make_humidity(history['weather_wind_mph'])
    translation = make_weather_detail(history['weather_detail'])
    history['weather_detail'] = make_weather(history['weather_detail'], translation)
    history['spread_favorite'] = make_humidity(history['spread_favorite'])
    history['over_under_line'] = make_humidity(history['over_under_line'])
    history.to_csv('history_no_nan.csv')
    # translation
    with open('weather_translations.csv', 'w') as f:
        for key in translation.keys():
            f.write("%s,%s\n"%(key,translation[key]))
    print(history.head())
    # history.to_csv('history_')

if __name__ == "__main__":
    print(main())
