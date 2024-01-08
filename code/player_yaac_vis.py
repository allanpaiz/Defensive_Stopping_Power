# Source: https://github.com/mckayjohns/youtube-videos/blob/main/code/plottable_tables.ipynb
# Changed and updated to fit my project

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from plottable import ColumnDefinition, Table
from plottable.plots import image
import numpy as np

defender_yaac = pd.read_csv('yaac.csv')
tackles = pd.read_csv('tackles.csv')
game_count_df = pd.read_csv('defender_game_play_count.csv')

defender_yaac.drop(columns=['gameId','gameCount'], inplace=True)
defender_yaac = defender_yaac[defender_yaac['position'] != 'WR']
defender_yaac['yaacCount'] = pd.to_numeric(defender_yaac['yaacCount'])
grouped = defender_yaac.groupby('nflId', as_index=False).agg({'totalYaac':'sum', 'yaacCount':'sum'})
sorted_df = defender_yaac.sort_values(by=['nflId', 'yaacCount'], ascending=[True, False])
max_yaac = sorted_df.groupby('nflId', as_index=False).first()
defender_yaac = pd.merge(grouped[['nflId', 'totalYaac', 'yaacCount']], max_yaac[['nflId', 'displayName', 'jerseyNumber', 'club', 'position']], on='nflId')
tackles = tackles.groupby('nflId', as_index=False).agg({'playId':'count', 'tackle':'sum', 'assist':'sum', 'pff_missedTackle':'sum'})
defender_yaac = pd.merge(defender_yaac, tackles, on='nflId', how='left')
game_count_df['nflId'] = game_count_df['nflId'].astype(int)
defender_yaac = pd.merge(defender_yaac, game_count_df, on='nflId', how='left')

defender_yaac['avgYaac'] = defender_yaac['totalYaac'] / defender_yaac['yaacCount']

dl_df = defender_yaac[defender_yaac['position'].isin(['DT', 'NT', 'DE'])]

def create_leaderboard(group_df, min_yaac, min_snaps):
    group_df = group_df[group_df['yaacCount'] >= min_yaac]
    group_df = group_df[group_df['playCount'] >= min_snaps]
    group_df = group_df.sort_values(by='avgYaac', ascending=False)
    group_df['rank'] = np.arange(len(group_df), 0, -1) 
    group_df = group_df.sort_values(by='rank')
    # group_df['rank'] = range(1, len(group_df) + 1)
    return group_df.tail(20)

lb_leaderboard = create_leaderboard(dl_df, 40,100)
df = lb_leaderboard

df['avgYaac'] = df['avgYaac'].round(2)
df['totalYaac'] = df['totalYaac'].astype(int)
df.rename(columns={'rank': 'Rk', 'club': 'Team', 'position': 'Pos',
                   'displayName': 'Name', 'gameCount': 'GP', 'playCount': 'Snaps',
                   'yaacCount': 'yaac_count', 'totalYaac': 'yaac_total',
                   'avgYaac': 'yaac_avg', 'tackle': 'Tackle', 'assist': 'Assist'}, inplace=True)

df['badge'] = df['Team'].apply(
    lambda x: f"logos/{x}.png"
)
columns = ['Rk', 'badge', 'Pos', 'Name', 'GP', 'Snaps', 'yaac_count', 'yaac_total', 'yaac_avg', 'Tackle', 'Assist']
df = df[columns]

df['Tackle'] = df['Tackle'].astype(int)
df['Assist'] = df['Assist'].astype(int)

bg_color = "#FFFFFF"
text_color = "#000000"

plt.rcParams["text.color"] = text_color
plt.rcParams["font.family"] = "monospace"

col_defs = [
    ColumnDefinition(name="Rk", textprops={"ha": "center"}),
    ColumnDefinition(name="badge", textprops={"ha": "center", "va": "center", 'color': bg_color}, plot_fn=image),
    ColumnDefinition(name="Pos", textprops={"ha": "left", "weight": "bold"}),
    ColumnDefinition(name="Name", textprops={"ha": "left", "weight": "bold"}, width=2),
    ColumnDefinition(name="GP", textprops={"ha": "center"}),
    ColumnDefinition(name="Snaps", textprops={"ha": "center"}),
    ColumnDefinition(name="yaac_count", group="YAAC", textprops={"ha": "center"}),
    ColumnDefinition(name="yaac_total", group="YAAC", textprops={"ha": "center"}),
    ColumnDefinition(name="yaac_avg", cmap=matplotlib.cm.inferno, group="YAAC", textprops={"ha": "center"}),
    ColumnDefinition(name="Tackle", group="Box Score", textprops={"ha": "center"}),
    ColumnDefinition(name="Assist", group="Box Score", textprops={"ha": "center"}),
]

fig, ax = plt.subplots(figsize=(20, 12))
fig.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

plt.title("DT/NT/DE Leaderboard (min 100 snaps & 40 yaac_count)", fontsize=20, color=text_color, fontweight='bold')

table = Table(
    df,    column_definitions=col_defs,    index_col="Rk",
    row_dividers=True,    row_divider_kw={"linewidth": 1, "linestyle": (0, (1, 5))},
    footer_divider=True,    textprops={"fontsize": 14},    col_label_divider_kw={"linewidth": 1, "linestyle": "-"},
    column_border_kw={"linewidth": .5, "linestyle": "-"},
    ax=ax,
)

plt.show()