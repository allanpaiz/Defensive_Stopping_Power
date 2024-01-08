import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

tracking_closest_defender_df = pd.read_csv('first_contact.csv')
background_color = "#F0F0F0"

df = tracking_closest_defender_df.copy()
df['Potential Impact Defenders'] = df['isTackler'] | df['isAssister'] | df['isMissedTackler'] | df['isFumbler']
df['Non Impact Defenders'] = ~(df['isTackler'] | df['isAssister'] | df['isMissedTackler'] | df['isFumbler'])

def plot_combined_heatmaps_with_improved_separation(df, bw_adjust=0.3, alpha=1):
    min_x = df['rel_X'].min()
    max_x = df['rel_X'].max()
    min_y = df['rel_Y'].min()
    max_y = df['rel_Y'].max()
    min_sx = df['Sx_diff'].min()
    max_sx = df['Sx_diff'].max()
    min_sy = df['Sy_diff'].min()
    max_sy = df['Sy_diff'].max()

    fig, ax = plt.subplots(2, 2, figsize=(16, 16), gridspec_kw={'hspace': 0.4, 'wspace': 0.4})
    plt.style.use({'figure.facecolor': 'F0F0F0'})

    sns.kdeplot(x=df[df['Potential Impact Defenders']]['rel_X'], y=df[df['Potential Impact Defenders']]['rel_Y'], cmap="Reds", fill=True, bw_adjust=bw_adjust, alpha=alpha, ax=ax[0, 0])
    ax[0, 0].set_title('Defender Position Heatmap for Potential Impact Defenders')
    ax[0, 0].set_xlim(min_x, max_x)
    ax[0, 0].set_ylim(min_y, max_y)
    ax[0, 0].set_xlabel('Relative X Position')
    ax[0, 0].set_ylabel('Relative Y Position')
    ax[0, 0].axhline(0, color='#000000', linewidth=1)
    ax[0, 0].axvline(0, color='#000000', linewidth=1)

    sns.kdeplot(x=df[df['Non Impact Defenders']]['rel_X'], y=df[df['Non Impact Defenders']]['rel_Y'], cmap="Blues", fill=True, bw_adjust=bw_adjust, alpha=alpha, ax=ax[0, 1])
    ax[0, 1].set_title('Defender Position Heatmap for Non Impact Defenders')
    ax[0, 1].set_xlim(min_x, max_x)
    ax[0, 1].set_ylim(min_y, max_y)
    ax[0, 1].set_xlabel('Relative X Position')
    ax[0, 1].set_ylabel('Relative Y Position')
    ax[0, 1].axhline(0, color='#000000', linewidth=1)
    ax[0, 1].axvline(0, color='#000000', linewidth=1)

    sns.kdeplot(x=df[df['Potential Impact Defenders']]['Sx_diff'], y=df[df['Potential Impact Defenders']]['Sy_diff'], cmap="Reds", fill=True, bw_adjust=bw_adjust, alpha=alpha, ax=ax[1, 0])
    ax[1, 0].set_title('Velocity Difference Heatmap for Potential Impact Defenders')
    ax[1, 0].set_xlim(min_sx, max_sx)
    ax[1, 0].set_ylim(min_sy, max_sy)
    ax[1, 0].set_xlabel('Sx_diff')
    ax[1, 0].set_ylabel('Sy_diff')
    ax[1, 0].axhline(0, color='#000000', linewidth=1)
    ax[1, 0].axvline(0, color='#000000', linewidth=1)

    sns.kdeplot(x=df[df['Non Impact Defenders']]['Sx_diff'], y=df[df['Non Impact Defenders']]['Sy_diff'], cmap="Blues", fill=True, bw_adjust=bw_adjust, alpha=alpha, ax=ax[1, 1])
    ax[1, 1].set_title('Velocity Difference Heatmap for Non Impact Defenders')
    ax[1, 1].set_xlim(min_sx, max_sx)
    ax[1, 1].set_ylim(min_sy, max_sy)
    ax[1, 1].set_xlabel('Sx_diff')
    ax[1, 1].set_ylabel('Sy_diff')
    ax[1, 1].axhline(0, color='#000000', linewidth=1)
    ax[1, 1].axvline(0, color='#000000', linewidth=1)

    plt.tight_layout(pad=1)
    plt.show()

plot_combined_heatmaps_with_improved_separation(df, bw_adjust=0.3, alpha=1)