# Letterboxd Data Conversion
## Overview
Creating a project in order to convert and update my personal Letterboxd movie-watching data so that I can create new and fun statistics with it. Upon completion,
new entries will be added automatically weekly, updating a Google sheet which then updates a Tableau dashboard that is in progress.

## How it works
The generator script takes the raw `diary.csv` that I downloaded directly from Letterboxd and then extracts and formats the data I want out of it.
Additionally, it checks my Letterboxd RSS page for updates and adds those entries in the same format.

## Challenges
The inital `diary.csv` had a different format than the RSS page so I had to reconcile those two. Initially, it was creating duplicate entries for the same watch log.
The RSS page also only includes watch from the past 50 entries or so.

With that, a problem I'm currently unsure how to fix is if I go and edit a rating byond the RSS timeframe, the spreadsheet does not
update with that new rating. Hypothetically, I would have to download a whole new CSV from Letterboxd each time and create a new spreadsheet based off of it which
defeats the purpose of having an automatically updating spreadsheet. Currently there's no way to access that data purely online.
