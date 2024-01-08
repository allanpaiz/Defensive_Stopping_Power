import pandas as pd
import math
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split

tracking_df_og = pd.read_csv('first_contact.csv')
ball_carrier_data = tracking_df_og[tracking_df_og['isBallCarrier'] == True][['game_play_ID', 's', 'Dir_std']]
speed_mapping = ball_carrier_data.set_index('game_play_ID')['s'].to_dict()
direction_mapping = ball_carrier_data.set_index('game_play_ID')['Dir_std'].to_dict()

def assign_ball_carrier_features(row):
    if not row['isPossessionTeam']:
        game_play_id = row['game_play_ID']
        return speed_mapping.get(game_play_id), direction_mapping.get(game_play_id)
    return None, None
tracking_df_og[['S_bc', 'Dir_std_bc']] = tracking_df_og.apply(assign_ball_carrier_features, axis=1, result_type='expand')
tracking_df = tracking_df_og[tracking_df_og['isPossessionTeam'] == False]

columns = ['game_play_ID','nflId', 'isTackler', 'isAssister',
       'isMissedTackler', 'isFumbler','s', 'X_std',
       'Y_std', 'Dir_std', 'dist_to_BC', 'isClosest',
       'X_std_bc', 'Y_std_bc','S_bc','Dir_std_bc']
tracking_df = tracking_df[columns]

tracking_df['rel_X'] = tracking_df['X_std'] - tracking_df['X_std_bc']
tracking_df['rel_Y'] = tracking_df['Y_std'] - tracking_df['Y_std_bc']
tracking_df['Sx'] = tracking_df['s']*tracking_df['Dir_std'].apply(math.cos)
tracking_df['Sy'] = tracking_df['s']*tracking_df['Dir_std'].apply(math.sin)
tracking_df['Sx_bc'] = tracking_df['S_bc']*tracking_df['Dir_std_bc'].apply(math.cos)
tracking_df['Sy_bc'] = tracking_df['S_bc']*tracking_df['Dir_std_bc'].apply(math.sin)
tracking_df['minus_bc_x'] = tracking_df['X_std_bc'] - tracking_df['X_std']
tracking_df['minus_bc_y'] = tracking_df['Y_std_bc'] - tracking_df['Y_std']
tracking_df['minus_bc_Sx'] = tracking_df['Sx_bc'] - tracking_df['Sx']
tracking_df['minus_bc_Sy'] = tracking_df['Sy_bc'] - tracking_df['Sy']

tracking_level_features = [
    'game_play_ID',
    'X_std',
    'Y_std',
    'rel_X',
    'rel_Y',
    'Sx',
    'Sy',
    'minus_bc_x',
    'minus_bc_y',
    'minus_bc_Sx',
    'minus_bc_Sy',
    'isTackler',
    'isAssister',
    'isMissedTackler',
    'isFumbler',
    'isClosest'
]
tracking_df = tracking_df[tracking_level_features]

columns_to_convert = ['isTackler', 'isAssister', 'isMissedTackler', 'isFumbler', 'isClosest']
tracking_df[columns_to_convert] = tracking_df[columns_to_convert].astype(int)

tracking_df['inContact'] = ((tracking_df['isTackler'] | tracking_df['isAssister'] | 
                             tracking_df['isMissedTackler'] | tracking_df['isFumbler']) & 
                             tracking_df['isClosest']).astype(int)

tracking_df.drop(columns=['isTackler', 'isAssister', 'isMissedTackler', 'isFumbler', 'isClosest'], inplace=True)

X = tracking_df.drop(['game_play_ID', 'inContact'], axis=1)
y = tracking_df['inContact']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = Sequential()
model.add(Dense(10, input_dim=X_train.shape[1], activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=10, batch_size=10)
loss, accuracy = model.evaluate(X_test, y_test)
print(f'Accuracy: {accuracy}')

model.save('nn_001.h5')