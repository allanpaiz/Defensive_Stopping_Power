import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

tracking_df = pd.read_csv('24/data/resource/PCS.csv')

tracking_df = tracking_df[~tracking_df['isPossessionTeam']]
columns = [ 'game_play_ID', 'nflId', 'displayName', 'frameId', 'jerseyNumber', 'event', 'inContact']
tracking_df = tracking_df[columns]

max_contact = tracking_df.groupby(['game_play_ID', 'nflId'])['inContact'].transform('max')
tracking_df['peak'] = (tracking_df['inContact'] == max_contact) & (tracking_df['inContact'] > 0)
tracking_df['peak'] = tracking_df['peak'].astype(int)

def animate_contact_prediction(game_play_ID, df):
    game_data = df[df['game_play_ID'] == game_play_ID]
    defenders = game_data['nflId'].unique()

    if len(defenders) != 11:
        print("Error: There are not 11 defenders.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.tab20(np.linspace(0, 1, 20))
    lines = []

    for i, defender in enumerate(defenders):
        line, = ax.plot([], [], color=colors[i], label=f'{game_data[game_data["nflId"] == defender]["jerseyNumber"].iloc[0]} : {game_data[game_data["nflId"] == defender]["displayName"].iloc[0]}')
        lines.append(line)

    ax.set_xlim(0, game_data['frameId'].max())
    ax.set_ylim(0, 1)
    ax.set_xlabel('Frame ID (Time)')
    ax.set_ylabel('InContact Value')
    ax.legend()

    ax.set_title(f'Predicted Contact Score for Game Play ID: {game_play_ID}')

    first_contact_frame = game_data[game_data['event'] == 'first_contact']['frameId'].unique()
    significant_event_frames = game_data[game_data['event'].isin(['tackle', 'out_of_bounds', 'touchdown'])]

    for fcf in first_contact_frame:
        ax.axvline(x=fcf, color='blue', linestyle='dotted')
        ax.text((fcf + .5) , .95, 'First Contact', verticalalignment='bottom', color='blue')

    for index, row in significant_event_frames.iterrows():
        ax.axvline(x=row['frameId'], color='red', linestyle='dotted')
        ax.text((row['frameId'] + .5) , .95, row['event'].capitalize(), verticalalignment='bottom', color='red')

    ax.axhline(y=0.25, color='grey', linestyle='dotted')
    ax.text(0, 0.25, ' 25% Prediction Threshold', verticalalignment='bottom', color='grey')

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def animate(frame):
        for i, defender in enumerate(defenders):
            defender_data = game_data[game_data['nflId'] == defender]
            x = defender_data['frameId']
            y = defender_data['inContact']
            lines[i].set_data(x[:frame], y[:frame])

        return lines

    frames = len(game_data['frameId'].unique()) + 30
    anim = FuncAnimation(fig, animate, init_func=init, frames=frames, interval=100, blit=True)

    anim.save(f'figures/{game_play_ID}.gif', writer='pillow', fps=10)
    plt.savefig(f'figures/{game_play_ID}_final.jpeg')

    plt.show()

    return anim

anim = animate_contact_prediction('2022100909_628', tracking_df)