import pandas as pd

plays = pd.read_csv('plays.csv')
tackles = pd.read_csv('tackles.csv')
tackles = pd.read_csv('tackles.csv')
players = pd.read_csv('players.csv')
games_df = pd.read_csv('games.csv')
tracking = pd.read_csv('tracking_post_PCS.csv')

def create_game_play_ID(plays_df, tackles_data):
    plays_df.insert(0, 'game_play_ID', plays_df['gameId'].astype(str) + '_' + plays_df['playId'].astype(str))
    plays_df.drop(columns=['gameId', 'playId'], inplace=True)
    tackles_data.insert(0, 'game_play_ID', tackles_data['gameId'].astype(str) + '_' + tackles_data['playId'].astype(str))
    tackles_data.drop(columns=['gameId', 'playId'], inplace=True)
    print('game_play_ID created')
    return plays_df, tackles_data

def remove_penalty_plays(plays_df, tracking_df, tackles_df):
    penalty_columns = ['penaltyYards', 'foulName1', 'foulName2', 'foulNFLId1', 'foulNFLId2']
    penalty_plays_df = plays_df[penalty_columns].notnull().any(axis=1)
    plays_df_no_penalties = plays_df[~penalty_plays_df].drop(columns=penalty_columns)
    tracking_df_no_penalties = tracking_df[~tracking_df['game_play_ID'].isin(plays_df[penalty_plays_df]['game_play_ID'])]
    tackles_df_no_penalties = tackles_df[~tackles_df['game_play_ID'].isin(plays_df[penalty_plays_df]['game_play_ID'])]
    print('penalty plays removed')
    return plays_df_no_penalties, tracking_df_no_penalties, tackles_df_no_penalties

plays, tackles = create_game_play_ID(plays, tackles)
plays_df_o, tracking_df_o, tackles_df_o = remove_penalty_plays(plays, tracking, tackles) 

tracking_defenders = tracking_df_o[tracking_df_o['isPossessionTeam'] == False]
tracking_ball_carriers = tracking_df_o[(tracking_df_o['isPossessionTeam'] == True) & (tracking_df_o['isBallCarrier'] == True)]

ball_carriers_relevant = tracking_ball_carriers[['game_play_ID', 'frameId', 'nflId', 'X_std']]
ball_carriers_relevant.rename(columns={'nflId': 'ballCarrierId', 'X_std': 'X_std_bc'}, inplace=True)
tracking_defenders = pd.merge(tracking_defenders, ball_carriers_relevant, on=['game_play_ID', 'frameId'])

def filter_tracking_frames(tracking_df, end_frame_events):
    first_end_frame = tracking_df[tracking_df['event'].isin(end_frame_events)] \
        .groupby(['game_play_ID', 'nflId'])['frameId'] \
        .min() \
        .reset_index() \
        .rename(columns={'frameId': 'first_end_frameId'})
    merged_df = tracking_df.merge(first_end_frame, on=['game_play_ID', 'nflId'], how='left')
    result_df = merged_df[merged_df['frameId'] <= merged_df['first_end_frameId']]
    result_df.drop(columns='first_end_frameId', inplace=True)

    return result_df

def create_end_frame_df(df, end_frame_events):
    end_frames = df[df['event'].isin(end_frame_events)]
    end_frame_df = end_frames.groupby('game_play_ID').agg({'frameId': 'min', 'X_std': 'first'}).reset_index()
    end_frame_df.rename(columns={'X_std': 'X_bc_eop'}, inplace=True)

    return end_frame_df

end_frame_events = ['tackle', 'out_of_bounds', 'touchdown']
filtered_tracking_df = filter_tracking_frames(tracking_defenders, end_frame_events)
ball_carrier_end_frame_df = create_end_frame_df(tracking_ball_carriers, end_frame_events)

tracking_defenders = tracking_defenders[tracking_defenders['inContact'] >= 0.25]

columns = ['game_play_ID', 'nflId', 'displayName', 'frameId', 'jerseyNumber', 'club', 'possessionTeam',
           'X_std', 'event', 'isPlayLeftToRight','inContact', 
           'ballCarrierId', 'X_std_bc']
tracking_defenders = tracking_defenders[columns]

max_contact_frame = tracking_defenders.groupby(['game_play_ID', 'nflId'])['inContact'].transform('idxmax')
tracking_defenders['pcm'] = 0
tracking_defenders.loc[max_contact_frame, 'pcm'] = 1
tracking_defenders = tracking_defenders[tracking_defenders['pcm'] == 1]
tracking_defenders = pd.merge(tracking_defenders, ball_carrier_end_frame_df, on='game_play_ID', how='left')

player_columns = ['nflId', 'position', 'height', 'weight']
players_df = players[player_columns]
feet = players_df['height'].str.split('-').str.get(0).astype(int) * 12
inches = players_df['height'].str.split('-').str.get(1).astype(int)
players_df['bmi'] = players_df['weight'] / ((feet + inches) / 2.54) ** 2

tracking_defenders = tracking_defenders[tracking_defenders['frameId_y'].notnull()]
tracking_defenders = tracking_defenders[tracking_defenders['X_bc_eop'].notnull()]

if tracking_defenders['isPlayLeftToRight'].iloc[0]:
    tracking_defenders['yaac'] = tracking_defenders['X_std_bc'] - tracking_defenders['X_bc_eop']
else:
    tracking_defenders['yaac'] = tracking_defenders['X_bc_eop'] - tracking_defenders['X_std_bc']

tracking_defenders = pd.merge(tracking_defenders, players_df, on='nflId', how='left')

columns = ['game_play_ID', 'nflId', 'displayName', 'jerseyNumber', 'club','position', 'bmi',
           'inContact', 'ballCarrierId', 'X_std_bc', 'X_bc_eop', 'yaac']
tracking_defenders = tracking_defenders[columns]

yaac_df = pd.read_csv('yaac.csv')

team_yaac_df = yaac_df.groupby(['game_play_ID', 'club']).agg(
    yaacTotal=('yaac', 'sum'),
    defCount=('nflId', 'nunique')
).reset_index()

ball_carrier_yaac = yaac_df.groupby(['game_play_ID', 'ballCarrierId']).agg(
    yaacTotal=('yaac', 'sum'),
    defCount=('nflId', 'nunique')
).reset_index()
ball_carrier_yaac['gameId'] = ball_carrier_yaac['game_play_ID'].str.split('_').str[0]
ball_carrier_yaac_game_count = ball_carrier_yaac.groupby('ballCarrierId')['gameId'].nunique().reset_index(name='gameCount')
ball_carrier_yaac = ball_carrier_yaac.merge(ball_carrier_yaac_game_count, on='ballCarrierId', how='left')

defender_yaac = yaac_df.groupby(['nflId', 'displayName', 'jerseyNumber', 'club', 'position', 'bmi']).agg(
    totalYaac=('yaac', 'sum'),
    yaacCount=('yaac', 'count')
).reset_index()
defender_yaac['nflId'] = defender_yaac['nflId'].astype(int)
defender_yaac['jerseyNumber'] = defender_yaac['jerseyNumber'].astype(int)

defender_yaac['gameId'] = yaac_df['game_play_ID'].str.split('_').str[0]
defender_yaac_game_count = defender_yaac.groupby('nflId')['gameId'].nunique().reset_index(name='gameCount')
defender_yaac = defender_yaac.merge(defender_yaac_game_count, on='nflId', how='left')

def create_game_play_ID(plays_df):
    plays_df.insert(0, 'game_play_ID', plays_df['gameId'].astype(str) + '_' + plays_df['playId'].astype(str))
    plays_df.drop(columns=['gameId', 'playId'], inplace=True)

    print('game_play_ID created')
    return plays_df

plays_df = create_game_play_ID(plays)
team_yaac_df['gameId'] = team_yaac_df['game_play_ID'].str.split('_').str[0]

columns = ['game_play_ID', 'playResult']
plays_df = plays_df[columns]
team_yaac_df = pd.merge(team_yaac_df, plays_df, on='game_play_ID', how='left')

team_yaac_df['yaacPerDefender'] = team_yaac_df['yaacTotal'] / team_yaac_df['defCount']
team_yaac_df['yaacPlusResult'] = team_yaac_df['yaacTotal'] + team_yaac_df['playResult']
team_yaac_df['yaacPRPerDef'] = team_yaac_df['yaacPlusResult'] / team_yaac_df['defCount']
team_yaac_df['defenderRatio'] = team_yaac_df['defCount'] / 11
team_yaac_df['dsp_ratio'] = team_yaac_df['yaacPRPerDef'] * team_yaac_df['defenderRatio']

team_game_yaac_df = team_yaac_df.groupby(['gameId', 'club']).agg(
    gameTotalYaac=('yaacTotal', 'sum'),
    gameTotalYaacPlusResult=('yaacPlusResult', 'sum'),
    gameTotalPlayResult=('playResult', 'sum'),
    gameAvgYaacPRPerDef=('yaacPRPerDef', 'mean'),
    gameAvgDSPRatio = ('dsp_ratio', 'mean'),
    gameAvgDSPSum = ('dsp_sum', 'mean')
).reset_index()

club_yaac_df = team_game_yaac_df.groupby('club').agg(
    seasonTotalYaac=('gameTotalYaac', 'sum'),
    seasonTotalYaacPlusResult=('gameTotalYaacPlusResult', 'sum'),
    seasonTotalPlayResult=('gameTotalPlayResult', 'sum'),
    seasonAvgYaacPRPerDef=('gameAvgYaacPRPerDef', 'mean'),
    seasonGameCount=('gameId', 'nunique'),
    seasonAvgDSPRatio=('gameAvgDSPRatio', 'mean'),
    seasonAvgDSPSum=('gameAvgDSPSum', 'mean')
).reset_index()

games_df['isTie'] = games_df['homeFinalScore'] == games_df['visitorFinalScore']
home_ties = games_df[games_df['isTie']].groupby('homeTeamAbbr').size()
visitor_ties = games_df[games_df['isTie']].groupby('visitorTeamAbbr').size()
combined_ties = home_ties.add(visitor_ties, fill_value=0).rename('Ties')
games_df['winningTeam'] = games_df.apply(lambda row: row['homeTeamAbbr'] if row['homeFinalScore'] > row['visitorFinalScore'] else (row['visitorTeamAbbr'] if row['homeFinalScore'] < row['visitorFinalScore'] else None), axis=1)
games_df['losingTeam'] = games_df.apply(lambda row: row['visitorTeamAbbr'] if row['homeFinalScore'] > row['visitorFinalScore'] else (row['homeTeamAbbr'] if row['homeFinalScore'] < row['visitorFinalScore'] else None), axis=1)
wins_losses = games_df['winningTeam'].value_counts().rename('Wins').to_frame().join(
    games_df['losingTeam'].value_counts().rename('Losses'),
    how='outer'
).fillna(0).astype(int)
games_df['homePointsAllowed'] = games_df['visitorFinalScore']
games_df['visitorPointsAllowed'] = games_df['homeFinalScore']
home_points_allowed = games_df.groupby('homeTeamAbbr')['homePointsAllowed'].sum()
visitor_points_allowed = games_df.groupby('visitorTeamAbbr')['visitorPointsAllowed'].sum()
combined_points_allowed = home_points_allowed.add(visitor_points_allowed, fill_value=0).rename('PointsAllowed')
club_yaac_df = club_yaac_df.merge(wins_losses, left_on='club', right_index=True, how='left')
club_yaac_df = club_yaac_df.merge(combined_ties, left_on='club', right_index=True, how='left')
club_yaac_df = club_yaac_df.merge(combined_points_allowed, left_on='club', right_index=True, how='left')

club_yaac_df['Ties'] = club_yaac_df['Ties'].fillna(0)
club_yaac_df['Wins'] += club_yaac_df['Ties'] * 0.5
club_yaac_df['Losses'] += club_yaac_df['Ties'] * 0.5
club_yaac_df.drop(columns=['Ties'], inplace=True)

club_yaac_df['seasonTotalYaac'] = club_yaac_df['seasonTotalYaac'].round(0).astype(int)
club_yaac_df['seasonTotalYaacPlusResult'] = club_yaac_df['seasonTotalYaacPlusResult'].round(0).astype(int)
club_yaac_df['seasonAvgYaacPRPerDef'] = club_yaac_df['seasonAvgYaacPRPerDef'].round(2)
club_yaac_df['seasonAvgDSPRatio'] = club_yaac_df['seasonAvgDSPRatio'].round(3)
club_yaac_df['seasonAvgDSPSum'] = club_yaac_df['seasonAvgDSPSum'].round(3)