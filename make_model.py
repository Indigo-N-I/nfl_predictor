import pandas as pd
import sklearn
import csv
import ast
from sklearn.linear_model import LinearRegression
from os import listdir
from os.path import isfile, join
from gplearn.genetic import SymbolicRegressor


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


def make_model(x_train, y_train, x_test= None, y_test= None, model = LinearRegression()):
    # print(x[:14], y[:14])
    reg = model.fit(x_train, y_train)
    # print(reg.score(x, y))
    # for a in reg.coef_:
        # print(a)
    print(reg.score(x_test, y_test))

def get_data(window_size = 0, test_years = [2022,2021,2013]):
    has_test = False
    has_train = False
    for f in listdir('data_windowed'):
        if '_' + str(window_size) + '_' in f:
            x, y = read_data('data_windowed\\' + f)
            # print(f'read {f}')
            if int(f[-8:-4]) > 1988:
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


if __name__ == "__main__":
    new_model = SymbolicRegressor(population_size = 20000, generations = 30, tournament_size = 300, random_state = 10, verbose=1,
        function_set = ('add','sub','mul','div','sqrt','log','abs','neg','inv','sin','cos','tan'))
    x_train, x_test, y_train, y_test = get_data(window_size = 4)
    y_train = y_train['score']
    y_test = y_test['score']
    # print(x_train)
    index = 0
    for a in x_train:
        print(str(index) + ":", a)
        index += 1
    print(x_train.head())
    print(y_train.head())
    new_model.fit(x_train, y_train)
    score_gp = new_model.score(x_test, y_test)
    print(score_gp)
    print(new_model._program)
    dot_data = new_model._program.export_graphviz()
    graph = graphviz.Source(dot_data)
    print(graph)


    # make_model(x_train, y_train, x_test, y_test, model = new_model)
