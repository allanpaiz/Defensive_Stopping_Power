# Defensive Stopping Power - 2024 NFL Big Data Bowl
### By Allan Paiz

## Table of Contents
- [Overview](#overview)
- [2024 Theme: Tackling](#2024-theme--tackling)
- [Solution](#solution)
- [Yards Allowed After Contact](#yards-allowed-after-contact)
- [Use](#use)
- [Conclusion](#conclusion)
<!--- - [Contact Information](#contact-information) -->

### Skills Demonstrated

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?logo=kaggle&logoColor=fff)](#)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=fff)](#)
[![NumPy](https://img.shields.io/badge/NumPy-4DABCF?logo=numpy&logoColor=fff)](#)
[![Keras](https://img.shields.io/badge/Keras-D00000?style=flat&logo=keras&logoColor=white)](#)
[![Scikit-learn](https://img.shields.io/badge/-scikit--learn-%23F7931E?logo=scikit-learn&logoColor=white)](#)
[![Matplotlib](https://custom-icon-badges.demolab.com/badge/Matplotlib-71D291?logo=matplotlib&logoColor=fff)](#)

[![Problem Solving](https://img.shields.io/badge/Problem%20Solving-2ECC71?style=flat&logo=code&logoColor=white)](#)
[![Data Analysis](https://img.shields.io/badge/Data%20Analysis-3498DB?style=flat&logo=chart-bar&logoColor=white)](#)
[![Machine Learning](https://img.shields.io/badge/Machine%20Learning-E74C3C?style=flat&logo=brain&logoColor=white)](#)
[![Data Visualization](https://img.shields.io/badge/Data%20Visualization-9B59B6?style=flat&logo=chart-line&logoColor=white)](#)
[![Feature Engineering](https://img.shields.io/badge/Feature%20Engineering-F1C40F?style=flat&logo=tools&logoColor=white)](#)

## Overview
This repository contains the code, figures and this summary for [my submission for the 2024 NFL Big Data Bowl](https://www.kaggle.com/code/allanpaiz/defensive-stopping-power) (Undergraduate Track).

I placed in the top 10 out of over 300 submissions, receiving $5,000 in prize money.

View the finalist announcement on [Kaggle](https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/discussion/472712) or [NFL.com](https://operations.nfl.com/gameday/analytics/big-data-bowl/2024-big-data-bowl-finalists/)

<!--- For more information on this project visit: -->
<!--- - My [**PLACEHOLDER** portfolio website](https://github.com/allanpaiz/Defensive_Stopping_Power) -->
<!--- - Or [**PLACEHOLDER** here](https://github.com/allanpaiz/Defensive_Stopping_Power) in pdf format. -->

## 2024 Theme : Tackling
The competition's tackling theme left me struggling to find a direction for my project.

Several of my ideas were limited by the provided datasets. The main issues I faced were:
1. The `first_contact` flag in the data was misleading. (See GIF below)
2. Besides the box score tackling data, there was **no information on all other contact** between ball carriers and defenders.

![Misleading first_contact flag examples](https://github.com/allanpaiz/Defensive_Stopping_Power/blob/main/figures/first_contact.gif)

## Solution
To address the tackling theme I wanted to create a method to **identify all contact**, or potential contact, between ball carriers and defenders.

I developed a **simple feedforward neural network** to serve as a contact detection model.

Using the `first_contact` flag along with player positions, speeds, directions, and box score data, I built a model that can **predict the probability of any defender tackling or attempting to tackle the ball carrier** throughout a play.

The example below illustrates the value of this model, with each line representing one of the eleven defenders.
The model helps fill the gaps in the data; on any given play, much more goes on between `first_contact` and the end of the play (`tackle`, in this case). 
![Probability of Contact Score (PCS) example over the course of a play](https://raw.githubusercontent.com/allanpaiz/Defensive_Stopping_Power/main/figures/PCS_example.gif)

# Yards Allowed After Contact
While the model and it's output is far from perfect, there are many unexplored ways to use this type of information.

So, I shifted my focus to developing a defensive metric called **Yards Allowed After Contact (YAAC)**.

The concept is simple: credit individual defenders with the yards *they allowed* on a play. 
Using the peaks from the model's predictions as the start of contact, we assign the yards gained after contact to the responsible defender.

Referencing the GIF above as an example, the table below is a sample of the YAAC's assigned:
| Number | Position | YAAC | Note | 
|:--:|:--|:--|:--|
| #58 | Linebacker | 11 yards | The first defender to miss a tackle. |
| #25 | Cornerback | ***NA*** | Was not involved in the play. |
| #36 | Safety | 1.5 yards | Tackled the running back. |

## Use
The potential for a fully developed model and YAAC metric is significant.
Whether building rosters, drafting prospects, or conducting defensive analysis, YAAC would be a valuable supplement alongside traditional metrics.

For example, a coach inserts defenders with low YAAC for short yardage situations, knowing they stop ball carriers close to the point of contact.
Or a front office can avoid signing a player with bad tackling techniques by filtering out players with a high YAAC average.

The leaderboard below ranks the 20 lowest average YAAC by defensive lineman, weeks 1 through 9, in the 2022 NFL Season.

Not surprisingly Cameron Heyward is at the top of the list, he was selected for his 6th Pro Bowl in the 2022 season.
Daron Payne, Jeffery Simmons, and Maxx Crosby, other 2022-Pro Bowl selections, also appear on this leaderboard.

I want to highlight the player in *20th place* as an example:
- He played **9** games and appeared in **351** plays (or snaps).
- The model predicts he contacted the ball carrier on **56** of those snaps.
- He allowed his opponents to gain a total of **72** yards after contact.
- On average, he stops the opponent within **1.29** yards of first contact.
- Traditional metrics credit him with **13** tackles and **12** assisted tackles.

![](https://raw.githubusercontent.com/allanpaiz/Defensive_Stopping_Power/refs/heads/main/figures/DL_leaderboard.png)

## Conclusion
Almost 2 years later, I look back and think about what I could have done differently from the code to the notebook. However, I still believe YAAC can easily be implemented and used for many purposes throughout the NFL and College Football analytics.

Metrics for defenders on all levels are rather stale. The industry has relied on tackles, assisted tackles, and other basic statistics to make big money decisions, despite having the resources to unlock new doors.
YAAC and other related metrics can add a much-needed layer of depth for defensive analytics, just as offensive players are evaluated by their individual efforts, with rushing or passing yards gained.

At the end of the day, this project taught me so much and really ignited my passion for applying computer science and mathematics to my other interests in creative ways.
- I started to improve my python programming and learned the pandas framework.
- I learned the importance of careful data processing and feature engineering for AI and ML models.
- After watching hundreds of plays throughout the process, the game slowed down for me improving my ability to analyze the game.
- I worked a lot on my writing, reporting, and visualization skills across a variety of mediums. 

Thank you for reading.

By Allan Paiz

<!--- ### Contact Information -->
<!--- Visit my [**PLACEHOLDER** portfolio website](https://github.com/allanpaiz/Defensive_Stopping_Power) for ways to contact me. -->

<!--- ## Extra Example
<!--- These GIF's didn't make the kaggle notebook cut, show the accuracy of the model's contact predictions. -->
<!--- ![](https://github.com/allanpaiz/Defensive_Stopping_Power/blob/main/figures/play.gif) -->
<!--- ![](https://github.com/allanpaiz/Defensive_Stopping_Power/blob/main/figures/graphs.gif) -->
