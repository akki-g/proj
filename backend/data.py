import pandas as pd
import os

cwd = os.getcwd()
print(cwd)
data_path = os.path.join(cwd, 'backend/data')

game = pd.read_csv(f'{data_path}/game_details.csv')
team = pd.read_csv(f'{data_path}/teams.csv')
player = pd.read_csv(f'{data_path}/players.csv')
player_game = pd.read_csv(f'{data_path}/player_box_scores.csv')

for df in [game, team, player, player_game]:
    print(df.columns.tolist())
    print(df.head(2))