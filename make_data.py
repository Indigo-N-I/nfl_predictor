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

def read_data(file, ignore_weather = True, drop_week = True):
    d = {}
    with open(file, 'r') as data:
        for line in data:
            d[line[:line.index(',')]] = ast.literal_eval(line[line.index(',')+1:-1])
            # print(line[:line.index(',')], line[line.index(',')+1:])
            # print(d)

    # print(d['x'].split('},'))
    # translate_to_dict(d['x'])
    x = pd.DataFrame.from_dict(d['x'])
    for col in x:
        if drop_week and 'schedule_week' in col:
            x = x.drop(col, axis = 1)
        if 'weather_detail' in col:
            if ignore_weather:
                 x = x.drop(col, axis = 1)
            else:
                x[col] = [ast.literal_eval(b) for b in x[col].tolist()]
    y = pd.DataFrame.from_dict(d['y'])
    return x, y

def make_model(x_train, y_train, x_test= None, y_test= None, model = LinearRegression()):
    # print(x[:14], y[:14])
    reg = model.fit(x_train, y_train)
    # print(reg.score(x, y))
    for a in reg.coef_:
        print(a)
        print('new line')
    print(reg.score(x_train, y_train))

def get_data(window_size = 0, test_years = [2022,2021,2013]):
    has_test = False
    has_train = False
    for f in listdir('data_windowed'):
        if '_' + str(window_size) + '_' in f:
            x, y = read_data('data_windowed\\' + f)
            # print(f'read {f}')
            if int(f[-8:-4]) in test_years:
                if not has_test:
                    has_test = True
                    x_test = x
                    y_test = y
                else:
                    x_test = pd.concat([x_test, x]).reset_index().drop('index', axis = 1)
                    y_test = pd.concat([y_test, y]).reset_index().drop('index', axis = 1)
            else:
                if not has_train:
                    has_train = True
                    x_train = x
                    y_train = y
                else:
                    x_train = pd.concat([x_train, x]).reset_index().drop('index', axis = 1)
                    y_train = pd.concat([y_train, y]).reset_index().drop('index', axis = 1)
    return x_train, x_test, y_train, y_test
    # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

def main():
    global teams
    teams = pd.read_csv(r'data\nfl_teams.csv')
    t = teams['team_name']
    for team in t:
        for year in range(1966, 2023):
            for win in [3,4,5,6,0,1,2]:
                    # print(f'working on {team} for year {year} on window {win}')
                    window(team, 1, year,win, get_all = True)
    '''
    to make the data:
        get each of the teams
        for each week the data will be
        y: [win, beat_spread, over_under]

    model:
        1. basic regression on just the week of
        2. windows of size 1 -> 6, of BOTH teams
        3. apply to linear regression (sk learn)
        4. apply to symbolic regression (gp learn)

    '''

if __name__ == "__main__":
    # x,y = read_data('data_windowed\Arizona Cardinals_0_1994.csv')
    # x_1,y_1 = read_data('data_windowed\Arizona Cardinals_0_1995.csv')

    # result = pd.concat([x,x_1]).reset_index()
    # result = result.drop('index', axis = 1)
    # print(result)
    # print(x)
    # print([ast.literal_eval(b) for b in x['weather_detail0'].tolist()])
    # print(ast.literal_eval(x['weather_detail0'][0]))
    # make_model(x,y)
    x_train, x_test, y_train, y_test = get_data(window_size = 4)
    # print(x_train)
    # print(y_train)
    # print(x_test)
    # print(y_test)
    make_model(x_train, y_train, x_test, y_test)
