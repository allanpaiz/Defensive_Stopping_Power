import pandas as pd
import plotly.graph_objects as go
import numpy as np
import base64
import os

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('ascii')

def create_main_scatter():

    club_yaac_df = pd.read_csv('yaac.csv')
    df = club_yaac_df.copy()

    scatter = go.Figure()

    scatter.update_xaxes(range=[min(df['seasonAvgDSPRatio']) - .009, max(df['seasonAvgDSPRatio']) + .009])
    scatter.update_yaxes(range=[min(df['PointsAllowed']) - 25, max(df['PointsAllowed']) + 25])

    scatter.update_layout(
        title={
            'text': "Season Average DSP vs Points Allowed (Week 1-9)",
            'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top',
            'font': {'size': 24}
        },
        xaxis_title="Average Defensive Stopping Power",
        yaxis_title="Points Allowed",
        xaxis=dict(title_font=dict(size=18), showgrid=True, gridwidth=1, gridcolor='rgba(10, 10, 10, 1)'),
        yaxis=dict(title_font=dict(size=18), showgrid=True, gridwidth=1, gridcolor='rgba(10, 10, 10, 1)'),
        plot_bgcolor='rgba(255, 255, 255, 0.1)',
        paper_bgcolor='rgba(255, 255, 255, 0.1)',
        font=dict(family="Arial", size=14, color="black")
    )

    scatter.add_trace(
        go.Scatter(
            x=df['seasonAvgDSPRatio'],
            y=df['PointsAllowed'],
            mode='markers',
            marker=dict(size=1, color='black'),
            text=df['club'],
            hoverinfo='text+x+y'
        )
    )

    annotations = [
        dict(text="Good Defensive Stopping Power", x=0.05, y=0.05, xref="paper", yref="paper",
            showarrow=False, font=dict(size=14, color="white"),
            bgcolor="rgba(22, 160, 133, 1)", bordercolor="black", borderwidth=1, opacity=1),
        dict(text="Bad Defensive Stopping Power", x=0.95, y=0.05, xref="paper", yref="paper",
            showarrow=False, font=dict(size=14, color="white"),
            bgcolor="rgba(150, 40, 27, 1)", bordercolor="black", borderwidth=1, opacity=1)
    ]

    scatter.update_layout(annotations=annotations)

    base_dir = "path_to_logos"

    for index, row in df.iterrows():
        club_name = row['club']
        image_path = os.path.join(base_dir, f"{club_name}.png")

        if os.path.exists(image_path):
            encoded_image = image_to_base64(image_path)

            scatter.add_layout_image(
                dict(
                    source=f"data:image/png;base64,{encoded_image}",
                    x=row['seasonAvgDSPRatio'],
                    y=row['PointsAllowed'],
                    sizex=15,
                    sizey=13,
                    xanchor="center",
                    yanchor="middle",
                    xref="x",
                    yref="y",
                    sizing="contain",
                    opacity=0.95,
                    layer="above"
                )
            )

    scatter.add_shape(type='line', x0=np.mean(df['seasonAvgDSPRatio']), x1=np.mean(df['seasonAvgDSPRatio']),
                        y0=min(df['PointsAllowed']) - 25, y1=max(df['PointsAllowed']) + 25,
                        xref='x', yref='y', line=dict(color='grey', dash='longdash'))
    scatter.add_shape(type='line', x0=min(df['seasonAvgDSPRatio']) - .009, x1=max(df['seasonAvgDSPRatio']) + .009,
                        y0=np.mean(df['PointsAllowed']), y1=np.mean(df['PointsAllowed']),
                        xref='x', yref='y', line=dict(color='grey', dash='longdash'))

    scatter.show()

create_main_scatter()