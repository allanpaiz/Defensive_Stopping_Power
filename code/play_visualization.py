# Source: https://www.kaggle.com/codehunting/plotly-animated-and-interactive-nfl-plays
# Changed and updated to fit my project

import pandas as pd
import numpy as np
import plotly.graph_objects as go

colors = {
    'ARI':["#97233F","#000000","#FFB612"], 
    'ATL':["#A71930","#000000","#A5ACAF"], 
    'BAL':["#241773","#000000"], 
    'BUF':["#00338D","#C60C30"], 
    'CAR':["#0085CA","#101820","#BFC0BF"], 
    'CHI':["#0B162A","#C83803"], 
    'CIN':["#FB4F14","#000000"], 
    'CLE':["#311D00","#FF3C00"], 
    'DAL':["#003594","#041E42","#869397"],
    'DEN':["#FB4F14","#002244"], 
    'DET':["#0076B6","#B0B7BC","#000000"], 
    'GB' :["#203731","#FFB612"], 
    'HOU':["#03202F","#A71930"], 
    'IND':["#002C5F","#A2AAAD"], 
    'JAX':["#101820","#D7A22A","#9F792C"], 
    'KC' :["#E31837","#FFB81C"], 
    'LA' :["#003594","#FFA300","#FF8200"], 
    'LAC':["#0080C6","#FFC20E","#FFFFFF"], 
    'LV' :["#000000","#A5ACAF"],
    'MIA':["#008E97","#FC4C02","#005778"], 
    'MIN':["#4F2683","#FFC62F"], 
    'NE' :["#002244","#C60C30","#B0B7BC"], 
    'NO' :["#101820","#D3BC8D"], 
    'NYG':["#0B2265","#A71930","#A5ACAF"], 
    'NYJ':["#125740","#000000","#FFFFFF"], 
    'PHI':["#004C54","#A5ACAF","#ACC0C6"], 
    'PIT':["#FFB612","#101820"], 
    'SEA':["#002244","#69BE28","#A5ACAF"], 
    'SF' :["#AA0000","#B3995D"],
    'TB' :["#D50A0A","#FF7900","#0A0A08"], 
    'TEN':["#0C2340","#4B92DB","#C8102E"], 
    'WAS':["#5A1414","#FFB612"], 
    'football':["#ff00dd","#663831"]
}

def hex_to_rgb_array(hex_color):
    return np.array(tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))) 

def ColorDistance(hex1,hex2):
    if hex1 == hex2:
        return 0
    rgb1 = hex_to_rgb_array(hex1)
    rgb2 = hex_to_rgb_array(hex2)
    rm = 0.5*(rgb1[0]+rgb2[0])
    d = abs(sum((2+rm,4,3-rm)*(rgb1-rgb2)**2))**0.5
    return d

def ColorPairs(team1,team2):
    color_array_1 = colors[team1]
    color_array_2 = colors[team2]
    if ColorDistance(color_array_1[0],color_array_2[0])<500:
        return {team1:[color_array_1[0],color_array_1[1]],team2:[color_array_2[1],color_array_2[0]],'football':colors['football']}
    else:
        return {team1:[color_array_1[0],color_array_1[1]],team2:[color_array_2[0],color_array_2[1]],'football':colors['football']}

def find_play_details(gameId, playId=None):
    details = {
        'week': None,
        'playDetails': None,
        'playDescription': None
    }
    matching_games = games_df[games_df['gameId'] == gameId]['week']
    if not matching_games.empty:
        details['week'] = matching_games.iloc[0]
    if playId is not None:
        matching_plays = plays_df[(plays_df['gameId'] == gameId) & (plays_df['playId'] == playId)]
        if not matching_plays.empty:
            play_details = matching_plays[['possessionTeam', 'defensiveTeam', 'quarter', 'down','gameClock','yardsToGo','absoluteYardlineNumber']]
            play_description = matching_plays[['playDescription']]
            details['playDescription'] = play_description.iloc[0].to_list()[0]
            details['playDetails'] = play_details.iloc[0].to_dict()

    return details

def animate_play(tracking_df, games,players,gameId,playId):
    details = find_play_details(gameId, playId)
    week = details['week']
    selected_game_df = games[games.gameId==gameId].copy()
    tracking_players_df = pd.merge(tracking_df,players,how="left",on = "nflId")
    selected_tracking_df = tracking_players_df[(tracking_players_df.playId==playId)&(tracking_players_df.gameId==gameId)].copy()
    sorted_frame_list = selected_tracking_df.frameId.unique()
    sorted_frame_list.sort()
    frame_event_dict = dict(zip(selected_tracking_df.frameId, selected_tracking_df.event))
    sorted_event_list = [frame_event_dict.get(frameId, '') if not pd.isna(frame_event_dict.get(frameId)) else '' for frameId in sorted_frame_list]
    team_combos = list(set(selected_tracking_df.club.unique())-set(["football"]))
    color_orders = ColorPairs(team_combos[0],team_combos[1])
    line_of_scrimmage = details['playDetails']['absoluteYardlineNumber']

    if selected_tracking_df.isPlayLeftToRight.values[0] == True:
        first_down_marker = line_of_scrimmage + details['playDetails']['yardsToGo']
    else:
        first_down_marker = line_of_scrimmage - details['playDetails']['yardsToGo']

    down = details['playDetails']['down']
    quarter = details['playDetails']['quarter']
    gameClock = details['playDetails']['gameClock']
    playDescription = details['playDescription']
    possessionTeam = details['playDetails']['possessionTeam']
    defensiveTeam = details['playDetails']['defensiveTeam']

    if len(playDescription.split(" "))>15 and len(playDescription)>115:
        playDescription = " ".join(playDescription.split(" ")[0:16]) + "<br>" + " ".join(playDescription.split(" ")[16:])

    updatemenus_dict = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 100, "redraw": False}, "fromcurrent": True, "transition": {"duration": 0}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]
    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 18},
            "prefix": "Frame:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 1, "t": 5},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    frames = []
    for frameId in sorted_frame_list:
        data = []
        data.append(
            go.Scatter(
                x=np.arange(20,110,10), 
                y=[5]*len(np.arange(20,110,10)),
                mode='text',
                text=list(map(str,list(np.arange(20, 61, 10)-10)+list(np.arange(40, 9, -10)))),
                textfont_size = 30,
                textfont_family = "Courier New, monospace",
                textfont_color = "#ffffff",
                showlegend=False,
                hoverinfo='none'
            )
        )
        data.append(
            go.Scatter(
                x=np.arange(20,110,10), 
                y=[53.5-5]*len(np.arange(20,110,10)),
                mode='text',
                text=list(map(str,list(np.arange(20, 61, 10)-10)+list(np.arange(40, 9, -10)))),
                textfont_size = 30,
                textfont_family = "Courier New, monospace",
                textfont_color = "#ffffff",
                showlegend=False,
                hoverinfo='none'
            )
        )

        data.append(
            go.Scatter(
                x=[line_of_scrimmage,line_of_scrimmage], 
                y=[0,53.5],
                line_dash='dash',
                line_color='blue',
                showlegend=False,
                hoverinfo='none'
            )
        )

        data.append(
            go.Scatter(
                x=[first_down_marker,first_down_marker], 
                y=[0,53.5],
                line_dash='dash',
                line_color='yellow',
                showlegend=False,
                hoverinfo='none'
            )
        )

        endzoneColors = {0:color_orders[selected_game_df.homeTeamAbbr.values[0]][0],
                         110:color_orders[selected_game_df.visitorTeamAbbr.values[0]][0]}
        for x_min in [0,110]:
            data.append(
                go.Scatter(
                    x=[x_min,x_min,x_min+10,x_min+10,x_min],
                    y=[0,53.5,53.5,0,0],
                    fill="toself",
                    fillcolor=endzoneColors[x_min],
                    mode="lines",
                    line=dict(
                        color="white",
                        width=3
                        ),
                    opacity=1,
                    showlegend= False,
                    hoverinfo ="skip"
                )
            )
        for team in selected_tracking_df.club.unique():
            plot_df = selected_tracking_df[(selected_tracking_df.club == team) & (selected_tracking_df.frameId == frameId)].copy()
            if team != "football":
                hover_text_array = []
                for index, row in plot_df.iterrows():

                    hover_text = "nflId:{}<br>displayName:{}<br>Player Speed:{} yd/s<br>Confidence:{}".format(
                        row["nflId"], row["displayName_x"], row["s"], row["pcs"]
                    )
                    hover_text_array.append(hover_text)

                    size = 10
                    opacity = 0.8
                    color = color_orders[team][0]
                    confidence = row["pcs"]

                    if confidence > 0.1:
                        color = "red"
                        additional_size = (confidence - 0.1) * 20
                        additional_opacity = (confidence - 0.1) * 0.8
                        size += additional_size
                        opacity += additional_opacity

                    data.append(go.Scatter(
                        x=[row["x"]],
                        y=[row["y"]],
                        mode='markers',
                        marker=dict(
                            color=color,
                            size=size,
                            opacity=min(opacity, 1),
                            line=dict(
                                width=2,
                                color=color_orders[team][1]
                            )
                        ),
                        name=team,
                        hoverinfo='text',
                        hovertext=hover_text
                    ))
            else:
                data.append(go.Scatter(
                    x=plot_df["x"], 
                    y=plot_df["y"],
                    mode='markers',
                    marker=dict(
                        color=color_orders[team][0],
                        line=dict(
                            width=2,
                            color=color_orders[team][1]
                        ),
                        size=10
                    ),
                    name=team,
                    hoverinfo='none'
                ))

        event = sorted_event_list[frameId-1]
        slider_step = {"args": [
            [frameId],
            {"frame": {"duration": 100, "redraw": False},
             "mode": "immediate",
             "transition": {"duration": 0}}
        ],
            "label": f'{str(frameId)} {event}',
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)
        frames.append(go.Frame(data=data, name=str(frameId)))

    scale=10
    layout = go.Layout(
        autosize=False,
        width=120*scale,
        height=60*scale,
        xaxis=dict(range=[0, 120], autorange=False, tickmode='array',tickvals=np.arange(10, 111, 5).tolist(),showticklabels=False),
        yaxis=dict(range=[0, 53.3], autorange=False,showgrid=False,showticklabels=False),

        plot_bgcolor='#00B140',
        title=f"GameId: {gameId} | PlayId: {playId} | Week: {week}<br>Possession Team: {possessionTeam} | Defensive Team: {defensiveTeam} | Clock: {gameClock} | {quarter}Q"
            +"<br>"*19+f"{playDescription}",
        updatemenus=updatemenus_dict,
        sliders = [sliders_dict]
    )

    fig = go.Figure(
        data=frames[0]["data"],
        layout= layout,
        frames=frames[1:]
    )

    for y_val in [0,53]:
        fig.add_annotation(
                x=first_down_marker,
                y=y_val,
                text=str(down),
                showarrow=False,
                font=dict(
                    family="Courier New, monospace",
                    size=16,
                    color="black"
                    ),
                align="center",
                bordercolor="black",
                borderwidth=2,
                borderpad=4,
                bgcolor="#ff7f0e",
                opacity=1
                )
        
    for x_min in [0,110]:
        if x_min == 0:
            angle = 270
            teamName=selected_game_df.homeTeamAbbr.values[0]
        else:
            angle = 90
            teamName=selected_game_df.visitorTeamAbbr.values[0]

        fig.add_annotation(
            x=x_min+5, y=53.5/2, text=teamName, showarrow=False,
            font=dict(
                family="Courier New, monospace", size=32,color="White"
                ),
            textangle = angle
        )
    return fig

games_df = pd.read_csv('games.csv')
players_df = pd.read_csv('players.csv')
plays_df = pd.read_csv('plays.csv')
tracking_df = pd.read_csv('tracking_post_PCS.csv')

animate_play(tracking_df,games_df,players_df,2022100909,628).show()