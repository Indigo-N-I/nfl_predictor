import pandas as pd
import sklearn


def main():
    teams = pd.read_csv('data\nfl_teams.csv')
    '''
    to make the data:
        get each of the teams
        for each week the data will be
        x: [schedule_week,schedule_playoff,is_home, is_fav, is_under, spread, over_under_line, stadium_neutral,weather_temperature,weather_wind_mph,weather_humidity,weather_detail]
        y: [win, beat_spread, over_under]

    model:
        1. basic regression on just the week of
        2. windows of size 1 -> 6, of BOTH teams
        3. apply to linear regression (sk learn)
        4. apply to symbolic regression (gp learn)

    '''

if __name__ == "__main__":
    main()
