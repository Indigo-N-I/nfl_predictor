import pandas as pd

def main():
    history = pd.read_csv('history_no_nan.csv')
    teams = pd.read_csv('nfl_teams.csv')

    for team in set(teams['team_name']):
        team_history = history[(history['team_home'] == team) | (history['team_away'] == team)]

        team_history.to_csv(f'{team}.csv')

if __name__ == '__main__':
    main()
