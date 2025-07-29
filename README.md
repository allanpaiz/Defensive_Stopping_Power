# Defensive Stopping Power
### 2024 NFL Big Data Bowl

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?logo=kaggle&logoColor=fff)](#)

[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=fff)](#)
[![NumPy](https://img.shields.io/badge/NumPy-4DABCF?logo=numpy&logoColor=fff)](#)
[![Scikit-learn](https://img.shields.io/badge/-scikit--learn-%23F7931E?logo=scikit-learn&logoColor=white)](#)
[![Matplotlib](https://custom-icon-badges.demolab.com/badge/Matplotlib-71D291?logo=matplotlib&logoColor=fff)](#)

## 

## Overview
This repository contains my submission for the 2024 NFL Big Data Bowl (Undergraduate Track).
<!-- You can find more about this project on my [portfolio website](https://github.com/allanpaiz/Defensive_Stopping_Power) -->
Or [here](https://github.com/allanpaiz/Defensive_Stopping_Power) in pdf format.

### Problem
The topic for the 2024 NFL Big Data Bowl was: **Help evaluate tackling tactics and strategy**

I struggled to find a direction for my project, on several occasions my ideas we limited by the provided datasets.
The two main problems I faced were:
1. The `first_contact` flag in the data was misleading.
2. 2. The data lacked other information on contact between ball carriers and defender
![](https://github.com/allanpaiz/Defensive_Stopping_Power/blob/main/figures/first_contact.gif)

### Solution
Stuff about the model
The project develops a contact detection model to identify interactions between the ball carrier and defenders using tracking data, then computes YAAC to quantify defensive performance post-contact.
I built a contact detection model to identify ball carrier-defender interactions, then computed the YAAC metric to measure yards gained after contact—highlighting defensive gaps.
![gif](https://raw.githubusercontent.com/allanpaiz/Defensive_Stopping_Power/main/code/PCS_example.gif)

### Impact
Stuff about YAAC
Yards Allowed After Contact (YAAC) in NFL plays.

### Links
[Link to Submission](https://www.kaggle.com/code/allanpaiz/defensive-stopping-power)

### [2024 NFL Big Data Bowl : Runner Up Submission ($5,000)](https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/discussion/472712)
### [NFL.com](https://operations.nfl.com/gameday/analytics/big-data-bowl/2024-big-data-bowl-finalists/)

#### Seeking Internships [[linkedin](https://www.linkedin.com/in/allan-paiz/)] [[email](apaiz@email.sc.edu)]

- Undergraduate Track Submission
- Allan Paiz
- University of South Carolina

### 

This project is centered around two objectives:
- **Developing The Contact Model**: Creating a model capable of identifying contact between the ball carrier and defenders throughout a play.
- **Leveraging The Contact Model**: Utilizing this model, the paper introduces metrics such as Yards Allowed After Contact (YAAC) and Defensive Stopping Power (DSP).
