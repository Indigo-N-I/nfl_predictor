import pandas as pd
import sklearn
import csv
import ast
from sklearn.linear_model import LinearRegression
from os import listdir
from os.path import isfile, join

def window(team, week, season, window_size, get_all = False):
    global teams
    team_data = pd.read_csv(f'data\{team}.csv')

    team_data = team_data[team_data['schedule_season'] == season]
    if str(week) not in set(team_data['schedule_week']):
        return None

    team_data['is_home'] = (team_data['team_home'] == team)
    team_data['is_away'] = (team_data['team_away'] == team)
    team_data['no_humidity'] = [float(a[1:-1].split(',')[-1]) for a in team_data['weather_humidity'][:]]
    team_data['weather_humidity'] = [float(a[1:-1].split(',')[0]) for a in team_data['weather_humidity'][:]]

    team_data['no_wind'] = [float(a[1:-1].split(',')[-1]) for a in team_data['weather_wind_mph'][:]]
    team_data['weather_wind_mph'] = [float(a[1:-1].split(',')[0]) for a in team_data['weather_wind_mph'][:]]

    team_data['score'] = team_data['score_home'] * team_data['is_home']
    team_data['score'] += team_data['score_away'] * team_data['is_away']

    team_data['no_spread'] = [float(a[1:-1].split(',')[-1]) for a in team_data['spread_favorite'][:]]
    team_data['spread'] = [float(a[1:-1].split(',')[0]) for a in team_data['spread_favorite'][:]]

    team_symbol = teams[teams['team_name'] == team]['team_id_pfr'].tolist()[0]

    team_data['is_fav'] = team_data['team_favorite_id'] == team_symbol

    team_data['no_over_under'] = [float(a[1:-1].split(',')[-1]) for a in team_data['over_under_line'][:]]
    team_data['over_under'] = [float(a[1:-1].split(',')[0]) for a in team_data['over_under_line'][:]]


    team_data['opp_score'] = team_data['score_home'] * team_data['is_away'] + team_data['score_away'] * team_data['is_home']

    def get_data_for_week(w):
        # print(f'getting data for week {w} with window {window_size}')
        min_index = team_data.index[team_data['schedule_week'] == str(1)].tolist()[0]
        if str(w) not in list(team_data['schedule_week']):
            # print('here')
            return None, None
        desired_index = team_data.index[team_data['schedule_week'] == str(w)].tolist()[0]
        # print(desired_index, window_size, min_index)
        if min_index > desired_index - window_size:
            # print(f"week {w} for {window_size} exits")
            return None, None

        data = team_data.iloc[[i - min_index for i in range(desired_index - window_size, desired_index + 1)]]
        x = {}

        for i in range(len(data)):
            for col in ['schedule_week', 'schedule_playoff', 'is_fav', 'no_over_under', 'no_over_under', 'spread', 'no_spread', 'stadium_neutral', 'no_wind', 'weather_wind_mph', 'no_humidity', 'weather_humidity', 'weather_detail', 'score', 'opp_score']:

                x[col + f'{i}'] = data.iloc[-(i+1)][col]
        # print(x)
        y = { 'score': x['score0'],
            'opp_score': x['opp_score0']
        }
        del x['score0']
        del x['opp_score0']
        return x, y

    if get_all:
        weeks = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,'Wildcard', 'Division', 'Conference', 'Superbowl']
    else:
        weeks = [week]

    data = {}
    xs = []
    ys = []
    print(weeks)
    for w in weeks:
        print(f'doing week {w}')
        x, y = get_data_for_week(w)
        # print(x,y)
        if x and y:
            xs.append(x)
            ys.append(y)

    data['x'] = xs
    data['y'] = ys

    with open(f'data_windowed\{team}_{window_size}_{season}.csv', 'w') as f:
        for key in data.keys():
            f.write("%s,%s\n"%(key,data[key]))

def main():
    global teams
    teams = pd.read_csv(r'data\nfl_teams.csv')
    t = teams['team_name']
    for team in t:
        for year in range(1966, 2023):
            for win in [3,4,5,6,0,1,2]:
                    # print(f'working on {team} for year {year} on window {win}')
                    window(team, 1, year,win, get_all = True)


if __name__ == "__main__":
    main()
