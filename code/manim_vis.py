from manim import *
import pandas as pd
import numpy as np

class ContactPredictionGraph(Scene):
    def construct(self):
        tracking_df = pd.read_csv('tracking_all.csv')

        game_play_id = '2022091801_3533'
        game_play_data = tracking_df[tracking_df['game_play_ID'] == game_play_id]
        players_to_plot = game_play_data[game_play_data['inContact'] > .1]['nflId'].unique()
        colors = [BLUE, GREEN, RED, YELLOW, PURPLE, ORANGE, PINK, TEAL, GOLD, MAROON, LIGHT_BROWN]

        max_frame = game_play_data['frameId'].max()

        graph = Axes(
            x_range=[0, max_frame, 1],
            y_range=[0, 1, 0.1],
            x_length=10,
            y_length=6,
            axis_config={"color": BLUE},
            tips=False
        )

        threshold_line = DashedLine(
            start=graph.c2p(0, 0.25), 
            end=graph.c2p(max_frame, 0.25), 
            color=GREY
        )
        threshold_label = Text("Threshold", font_size=18).next_to(threshold_line, RIGHT, buff=0.1)

        x_label = Text("Time (frameId)").scale(0.5).next_to(graph.x_axis, DOWN, buff=0.1)
        y_label = Text("Predicted Contact Score").scale(0.5).rotate(PI/2).next_to(graph.y_axis, LEFT, buff=0.1)
        self.add(graph, x_label, y_label)

        y_tick_values = [0, 1]
        y_tick_labels = ["0", "100"]
        for value, label_text in zip(y_tick_values, y_tick_labels):
            label = Text(label_text, font_size=24).next_to(graph.y_axis.n2p(value), LEFT)
            self.add(label)

        line_graphs = []
        max_points = []
        peak_mark_creations = []
        event_line_coordinates = []

        for idx, player_id in enumerate(players_to_plot):
            player_data = game_play_data[game_play_data['nflId'] == player_id]
            frameId_inContact_data = player_data[['frameId', 'inContact']].values.tolist()
            max_inContact = player_data[player_data['inContact'] > 0.25]['inContact'].max()
            if not np.isnan(max_inContact):
                max_frame = player_data[player_data['inContact'] == max_inContact]['frameId'].iloc[0]
                max_points.append((max_frame, max_inContact))

            x_values, y_values = zip(*frameId_inContact_data)
            color = colors[idx % len(colors)]

            line_graph = graph.plot_line_graph(
                x_values=x_values,
                y_values=y_values,
                line_color=color,
                add_vertex_dots=False,
            )
            line_graphs.append(line_graph)

        event_data = game_play_data[game_play_data['event'].notna()]
        event_frames = event_data[['frameId', 'event']].drop_duplicates()
        event_labels = []

        for _, row in event_frames.iterrows():
            frame_id = row['frameId']
            event_name = row['event']

            if event_name == 'first_contact':
                color = BLUE
            elif event_name in ['tackle', 'out_of_bounds', 'touchdown']:
                color = RED
            else:
                color = GREY

            if event_name in ['tackle', 'out_of_bounds', 'touchdown']:
                event_x, _, _ = graph.c2p(frame_id, 0)
                event_line_coordinates.append(event_x)
            
            line = DashedLine(
                start=graph.c2p(frame_id, 0), 
                end=graph.c2p(frame_id, 1), 
                color=color
            )

            label = Text(event_name, font_size=20, color=color).rotate(PI/2)
            next_frame_id = frame_id + 1
            label.move_to(graph.c2p(next_frame_id, 1) + np.array([0, -0.5, 0]))
            event_labels.append(label)
            self.add(line, label)

        self.play(*[Create(line) for line in line_graphs], run_time=6)

        contact_yardline_labels = []
        peak_mark_creations = []
        contact_yardline_label_anims = []

        tackle_event = next((event for event in event_frames.itertuples() if event.event == 'tackle'), None)
        tackle_x = None
        if tackle_event:
            tackle_x, _, _ = graph.c2p(tackle_event.frameId, 0)

        for max_frame, max_inContact in max_points:
            peak_x, peak_y, _ = graph.c2p(max_frame, max_inContact)

            peak_mark = Tex('x').scale(0.8).move_to([peak_x, peak_y, 0])
            peak_mark_final = Tex('x').scale(0.8).move_to([tackle_x, peak_y, 0])
            peak_mark_creation = Create(peak_mark)
            peak_mark_creation_2 = Create(peak_mark_final)
            peak_mark_creations.append(peak_mark_creation)
            peak_mark_creations.append(peak_mark_creation_2)

            yardline_label = MathTex(r"\text{contact}_X", font_size=20).next_to(peak_mark, UP + RIGHT, buff=0.1)
            yardline_label_creation = Write(yardline_label)
            contact_yardline_labels.append(yardline_label)
            contact_yardline_label_anims.append(yardline_label_creation)

            final_x_label = MathTex(r"\text{final}_X", font_size=20).move_to([tackle_x + .5, peak_y, 0])
            final_x_label_creation = Write(final_x_label)
            contact_yardline_labels.append(final_x_label)
            contact_yardline_label_anims.append(final_x_label_creation)

        self.wait(1)
        if event_labels:
            self.play(*[FadeOut(label) for label in event_labels])

        tackle_event = next((event for event in event_frames.itertuples() if event.event == 'tackle'), None)
        if tackle_event:
            tackle_x, _, _ = graph.c2p(tackle_event.frameId, 0)
            dead_ball_label = Text("End of Play Location", font_size=14, color=RED).move_to(graph.c2p(tackle_event.frameId + 1, 1) + np.array([0, -0.5, 0])).rotate(PI/2)
            self.play(Write(dead_ball_label),Create(threshold_line), Write(threshold_label))

        dotted_line_animations = []
        yaac_texts = []

        for max_frame, max_inContact in max_points:
            peak_x, peak_y, _ = graph.c2p(max_frame, max_inContact)
            for event_x in event_line_coordinates:
                start_point = [peak_x, peak_y, 0]
                end_point = [event_x, peak_y, 0]
                center_point = [(peak_x + event_x) / 2, (peak_y + .25), 0]

                # Create dotted line
                dotted_line = DashedLine(start=start_point, end=end_point, color=WHITE)
                dotted_line_animation = Create(dotted_line)
                dotted_line_animations.append(dotted_line_animation)

                yaac_text = Text("YAAC", font_size=16).move_to(center_point)
                yaac_texts.append(Write(yaac_text))

        peak_x, peak_y, _ = graph.c2p(max_frame, max_inContact)
        center_point = [(peak_x + event_x) / 2, (peak_y + .25), 0]
        yaac_formula_text = MathTex(r"\text{YAAC} = \text{final}_X - \text{contact}_X", font_size=24).move_to(center_point + DOWN * 1.5)  # Adjust vertical position

        self.play(*dotted_line_animations)
        self.play(*peak_mark_creations) 
        self.wait(1)

        self.play(*[FadeOut(line) for line in line_graphs], FadeOut(threshold_line), FadeOut(threshold_label), FadeOut(dead_ball_label))
        self.play(*contact_yardline_label_anims)
        self.play(Write(yaac_formula_text))
        self.play(*[FadeOut(label) for label in contact_yardline_labels])
        self.play(*yaac_texts)
        self.wait(2)
        self.play(FadeOut(yaac_formula_text))
        self.wait(2)