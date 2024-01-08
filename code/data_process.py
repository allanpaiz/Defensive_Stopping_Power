import pandas as pd
import numpy as np

games_data = pd.read_csv('games.csv')
players_data = pd.read_csv('players.csv')
plays_data = pd.read_csv('plays.csv')
tackles_data = pd.read_csv('tackles.csv')

def comibine_tracking_data():
    weeks = range(1, 10)
    tracking_files = [f'{week}.csv' for week in weeks]
    tracking_df_all = pd.concat((pd.read_csv(f) for f in tracking_files), ignore_index=True)
    tracking_df_all['jerseyNumber'] = tracking_df_all['jerseyNumber'].astype(int)
    tracking_df_all['nflId'] = tracking_df_all['nflId'].astype(int)
    return tracking_df_all

tracking_df = comibine_tracking_data()

def merge_games_data_and_plays_data(games_data, plays_data):
    return games_data.merge(plays_data, on='gameId', how='left')

plays_df = merge_games_data_and_plays_data(games_data, plays_data)
print('plays and games data sets merged')

def create_game_play_ID(plays_df, tracking_df, tackles_data):
    plays_df.insert(0, 'game_play_ID', plays_df['gameId'].astype(str) + '_' + plays_df['playId'].astype(str))
    plays_df.drop(columns=['gameId', 'playId'], inplace=True)
    tracking_df.insert(0, 'game_play_ID', tracking_df['gameId'].astype(str) + '_' + tracking_df['playId'].astype(str))
    tracking_df.drop(columns=['gameId', 'playId'], inplace=True)
    tackles_data.insert(0, 'game_play_ID', tackles_data['gameId'].astype(str) + '_' + tackles_data['playId'].astype(str))
    tackles_data.drop(columns=['gameId', 'playId'], inplace=True)

    return plays_df, tracking_df, tackles_data

plays_df, tracking_df, tackles_df = create_game_play_ID(plays_df, tracking_df, tackles_data)
print('game_play_ID created')

def remove_football(tracking_df):
    return tracking_df[tracking_df['displayName'].str.strip().str.lower() != 'football']

def label_ball_carrier(plays_df, tracking_df):
    plays_df_tracking_df_merged = tracking_df.merge(plays_df[['game_play_ID', 'ballCarrierId']],left_on='game_play_ID', right_on='game_play_ID', how='left')    
    plays_df_tracking_df_merged['isBallCarrier'] = plays_df_tracking_df_merged['nflId'] == plays_df_tracking_df_merged['ballCarrierId']
    plays_df_tracking_df_merged.drop(columns=['ballCarrierId'], inplace=True)
    
    print('ball carrier labeled')
    return plays_df_tracking_df_merged

def label_tackler(tracking_df, tackles_df):
    isTackler_df = tackles_df[tackles_df['tackle'] == 1][['game_play_ID', 'nflId']]
    isTackler_df.rename(columns={'nflId': 'tacklerId'}, inplace=True)
    isTackler_df_tracking_df_merged = tracking_df.merge(isTackler_df, on='game_play_ID', how='left')
    isTackler_df_tracking_df_merged['isTackler'] = isTackler_df_tracking_df_merged['nflId'] == isTackler_df_tracking_df_merged['tacklerId']
    isTackler_df_tracking_df_merged.drop(columns=['tacklerId'], inplace=True)

    print('tackler labeled')
    return isTackler_df_tracking_df_merged

def label_assister(tracking_df, tackles_df):
    isAssister_df = tackles_df[tackles_df['assist'] == 1].groupby('game_play_ID')['nflId'].apply(list).reset_index(name='assistIds')
    isAssister_df_tracking_df_merged = tracking_df.merge(isAssister_df, on='game_play_ID', how='left')
    isAssister_df_tracking_df_merged['isAssister'] = isAssister_df_tracking_df_merged.apply(lambda x: x['nflId'] in (x['assistIds'] if isinstance(x['assistIds'], list) else []), axis=1)
    isAssister_df_tracking_df_merged.drop(columns=['assistIds'], inplace=True)

    print('assister labeled')
    return isAssister_df_tracking_df_merged

def label_missed_tackler(tracking_df, tackles_df):
    isMissedTackler_df = tackles_df[tackles_df['pff_missedTackle'] == 1].groupby('game_play_ID')['nflId'].apply(list).reset_index(name='missedTackleIds')
    isMissedTackler_df_tracking_df_merged = tracking_df.merge(isMissedTackler_df , on='game_play_ID', how='left')
    isMissedTackler_df_tracking_df_merged['isMissedTackler'] = isMissedTackler_df_tracking_df_merged.apply(lambda x: x['nflId'] in (x['missedTackleIds'] if isinstance(x['missedTackleIds'], list) else []), axis=1)
    isMissedTackler_df_tracking_df_merged.drop(columns=['missedTackleIds'], inplace=True)

    print('missed tackler labeled')
    return isMissedTackler_df_tracking_df_merged

def label_forced_fumbler(tracking_df, tackles_df):
    isFumbler_df = tackles_df[tackles_df['forcedFumble'] == 1][['game_play_ID', 'nflId']]
    isFumbler_df.rename(columns={'nflId': 'fumblerId'}, inplace=True)
    isFumbler_df_tracking_df_merged = tracking_df.merge(isFumbler_df, on='game_play_ID', how='left')
    isFumbler_df_tracking_df_merged['isFumbler'] = isFumbler_df_tracking_df_merged['nflId'] == isFumbler_df_tracking_df_merged['fumblerId']
    isFumbler_df_tracking_df_merged.drop(columns=['fumblerId'], inplace=True)

    print('forced fumbler labeled')
    return isFumbler_df_tracking_df_merged

def label_possession_team(plays_df, tracking_df):
    plays_df_tracking_df_merged = tracking_df.merge(plays_df[['game_play_ID', 'possessionTeam']], on='game_play_ID', how='left')
    plays_df_tracking_df_merged['isPossessionTeam'] = plays_df_tracking_df_merged['club'] == plays_df_tracking_df_merged['possessionTeam']
    plays_df_tracking_df_merged.drop(columns=['possessionTeam'], inplace=True)

    print('possession team labeled')
    return plays_df_tracking_df_merged

def label_play_direction(tracking_df):
    tracking_df['isPlayLeftToRight'] = tracking_df['playDirection'].apply(lambda val: val.strip().lower() == 'right')
    tracking_df.drop(columns=['playDirection'], inplace=True)

    print('play direction labeled')
    return tracking_df

def standardize_play_direction(tracking_df):
    tracking_df['Dir_rad'] = np.radians(90 - tracking_df['dir'])
    tracking_df['X_std'] = tracking_df['x']
    tracking_df.loc[~tracking_df['isPlayLeftToRight'], 'X_std'] = 120 - tracking_df.loc[~tracking_df['isPlayLeftToRight'], 'x']
    tracking_df['Y_std'] = tracking_df['y']
    tracking_df.loc[~tracking_df['isPlayLeftToRight'], 'Y_std'] = (160/3) - tracking_df.loc[~tracking_df['isPlayLeftToRight'], 'y']
    tracking_df['Dir_std'] = tracking_df['Dir_rad']
    tracking_df.loc[~tracking_df['isPlayLeftToRight'], 'Dir_std'] = np.mod(np.pi + tracking_df.loc[~tracking_df['isPlayLeftToRight'], 'Dir_rad'], 2 * np.pi)
    tracking_df.loc[tracking_df['isPossessionTeam'] & tracking_df['Dir_std'].isna(), 'Dir_std'] = 0.0
    tracking_df.loc[~tracking_df['isPossessionTeam'] & tracking_df['Dir_std'].isna(), 'Dir_std'] = np.pi

    print('play direction standardized')
    return tracking_df 

def assign_ball_carrier_features(tracking_df):
    bc_cols = ['X_std_bc', 'Y_std_bc', 'S_bc', 'Dir_std_bc']
    if not all(col in tracking_df.columns for col in bc_cols):
        ball_carrier_data = tracking_df[tracking_df['isBallCarrier'] == True][['frameId', 'X_std', 'Y_std', 's', 'Dir_std']]
        ball_carrier_data.rename(columns=dict(zip(['X_std', 'Y_std', 's', 'Dir_std'], bc_cols)), inplace=True)
        tracking_df = tracking_df.merge(ball_carrier_data, on='frameId', how='left')

    print('ball carrier features assigned')
    return tracking_df

def label_closest_defender(tracking_df):
    first_contact_df = tracking_df[tracking_df['event'] == 'first_contact']
    ball_carrier_positions_df = first_contact_df[first_contact_df['isBallCarrier']].groupby('game_play_ID')[['X_std', 'Y_std','Dir_std','s']].mean()
    ball_carrier_positions_df_first_contact_df_merged = first_contact_df.merge(ball_carrier_positions_df, on='game_play_ID', how='left', suffixes=('', '_bc'))

    def calculate_distance(row):
        if not row['isPossessionTeam']:
            return np.sqrt((row['X_std'] - row['X_std_bc'])**2 + (row['Y_std'] - row['Y_std_bc'])**2)
        else:
            return np.nan
        
    ball_carrier_positions_df_first_contact_df_merged['dist_to_BC'] = ball_carrier_positions_df_first_contact_df_merged.apply(calculate_distance, axis=1)
    closest_defender_distance = ball_carrier_positions_df_first_contact_df_merged.groupby(['game_play_ID', 'frameId'])['dist_to_BC'].idxmin()
    ball_carrier_positions_df_first_contact_df_merged['isClosest'] = False
    ball_carrier_positions_df_first_contact_df_merged.loc[closest_defender_distance, 'isClosest'] = True

    print('closest defender labeled')
    return ball_carrier_positions_df_first_contact_df_merged

def filter_tracking_frames(tracking_df, start_frame, end_frame):
    start_frame_id = tracking_df[tracking_df['event'].isin(start_frame)]['frameId'].min()
    end_frame_id = tracking_df[tracking_df['event'].isin(end_frame)]['frameId'].max()

    if pd.notna(start_frame_id) and pd.notna(end_frame_id):
        return tracking_df[(tracking_df['frameId'] >= start_frame_id) & (tracking_df['frameId'] <= end_frame_id)]
    else:
        return pd.DataFrame()

def remove_penalty_plays(plays_df, tracking_df, tackles_df):
    penalty_columns = ['penaltyYards', 'foulName1', 'foulName2', 'foulNFLId1', 'foulNFLId2']
    penalty_plays_df = plays_df[penalty_columns].notnull().any(axis=1)
    plays_df_no_penalties = plays_df[~penalty_plays_df].drop(columns=penalty_columns)
    tracking_df_no_penalties = tracking_df[~tracking_df['playId'].isin(plays_df[penalty_plays_df]['playId'])]
    tackles_df_no_penalties = tackles_df[~tackles_df['playId'].isin(plays_df[penalty_plays_df]['playId'])]

    print('penalty plays removed')
    return plays_df_no_penalties, tracking_df_no_penalties, tackles_df_no_penalties

def remove_plays_with_unwanted_events(plays_df, tracking_df, tackles_df, unwanted_events):
    play_ids_of_unwanted_events = tracking_df[tracking_df['event'].isin(unwanted_events)]['playId'].unique()
    plays_df_filtered = plays_df[~plays_df['playId'].isin(play_ids_of_unwanted_events)]  
    tracking_df_filtered = tracking_df[~tracking_df['playId'].isin(play_ids_of_unwanted_events)]
    tackles_df_filtered = tackles_df[~tackles_df['playId'].isin(play_ids_of_unwanted_events)]

    print('plays with unwanted events removed')
    return plays_df_filtered, tracking_df_filtered, tackles_df_filtered

def clean_columns(df, columns_to_keep):
    return df[columns_to_keep]

def filter_tracking_for_first_contact(tracking_df):
    tracking_df_first_contact = tracking_df[tracking_df['event'] == 'first_contact']

    print('tracking filtered for first contact')
    return tracking_df_first_contact

def filter_defenders_and_ball_carrier(tracking_df):
    filtered_df = tracking_df[(tracking_df['isPossessionTeam'] == False) | (tracking_df['isBallCarrier'] == True)]

    print('tracking filtered for defenders and ball carrier')
    return filtered_df

def filter_closest_defender_and_ball_carrier(tracking_df):
    filtered_df = tracking_df[(tracking_df['isClosest'] == True) | (tracking_df['isBallCarrier'] == True)]

    print('tracking filtered for closest defender and ball carrier')
    return filtered_df

def filter_out_ball_carrier(tracking_df):
    filtered_df = tracking_df[tracking_df['isBallCarrier'] == False]

    print('ball carrier filtered out')
    return filtered_df

def exclude_specific_game_plays(dataframe):
    exclude_list =  ['2022091809_1610', '2022110608_2351', '2022091113_2954', '2022103100_1689', '2022092500_808',
                '2022103004_2106', '2022100905_2546', '2022091809_2235', '2022091113_3139', '2022091102_4019',
                '2022091809_1310', '2022100209,1581', '2022100907_871', '2022100209_1581']
    filtered_df = dataframe[~dataframe['game_play_ID'].isin(exclude_list)]

    print('specific game plays excluded')
    return filtered_df

def compute_relative_positions(closest_defenders):
    closest_defenders['rel_X'] = closest_defenders['X_std'] - closest_defenders['X_std_bc']
    closest_defenders['rel_Y'] = closest_defenders['Y_std'] - closest_defenders['Y_std_bc']

    print('relative positions computed')
    return closest_defenders

def calculate_speed_components_np(tracking_df):
    dir_rad = np.radians(tracking_df['Dir_std'])
    dir_bc_rad = np.radians(tracking_df['Dir_std_bc'])
    tracking_df['Sx'] = tracking_df['s'] * np.cos(dir_rad)
    tracking_df['Sy'] = tracking_df['s'] * np.sin(dir_rad)
    tracking_df['Sx_bc'] = tracking_df['s_bc'] * np.cos(dir_bc_rad)
    tracking_df['Sy_bc'] = tracking_df['s_bc'] * np.sin(dir_bc_rad)

    print('speed components calculated')
    return tracking_df

def create_test_df(tracking_df):
    unique_ids = tracking_df['game_play_ID'].unique()
    num_ids = min(20, len(unique_ids))
    random_ids = np.random.choice(unique_ids, num_ids, replace=False)
    test_df = tracking_df[tracking_df['game_play_ID'].isin(random_ids)].copy()

    return test_df

def filter_closest_defenders(tracking_df):
    filtered_df = tracking_df[(tracking_df['isClosest'] == True) | (tracking_df['isBallCarrier'] == True)]

    print('tracking filtered for closest defenders and ball carrier')
    return filtered_df

def calculate_relative_metrics(tracking_df):
    tracking_df['X_diff'] = tracking_df['X_std_bc'] - tracking_df['X_std']
    tracking_df['Y_diff'] = tracking_df['Y_std_bc'] - tracking_df['Y_std']
    tracking_df['Sx_diff'] = tracking_df['Sx_bc'] - tracking_df['Sx']
    tracking_df['Sy_diff'] = tracking_df['Sy_bc'] - tracking_df['Sy']

    return tracking_df

def summarize_dataframe(df):
    print("Shape of DataFrame:", df.shape)
    print("\nColumns in DataFrame:", df.columns.tolist())

    print("\nFirst 10 rows:")
    print(df.head(10))

    print("\nRandom sample of 10 rows:")
    print(df.sample(10))

    print("\nDescriptive Statistics:")
    print(df.describe())

def attach_ball_carrier_info(tracking_df):
    ball_carrier_df = tracking_df[tracking_df['isBallCarrier']]
    ball_carrier_X_std = ball_carrier_df.groupby('game_play_ID')['X_std'].mean().reset_index()
    ball_carrier_X_std.columns = ['game_play_ID', 'X_std_bc']
    ball_carrier_ids = ball_carrier_df.groupby('game_play_ID')['nflId'].first().reset_index()
    ball_carrier_ids.columns = ['game_play_ID', 'ballCarrierId']

    tracking_df = tracking_df.merge(ball_carrier_ids, on='game_play_ID', how='left')
    tracking_df = tracking_df.merge(ball_carrier_X_std, on='game_play_ID', how='left')
    tracking_df = tracking_df[~tracking_df['isBallCarrier']]
    tracking_df .drop(columns=['isBallCarrier'], inplace=True)

    return tracking_df

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