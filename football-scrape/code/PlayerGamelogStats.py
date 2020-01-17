#!/usr/bin/python
import os
import gc
import pandas as pd
import psutil
from google.cloud import bigquery  # Imports the Google Cloud client library
from PlayerGamelogUtil import PlayerGamelogUtil

GAMELOG_STATS_FILENAME = 'player_gamelog_stats.csv'


def write_to_file(df):
    df.to_csv(os.path.join(files_dir, GAMELOG_STATS_FILENAME), index=False, encoding='utf-8')
    del df


# constants
dir_name = os.path.dirname(__file__)  # project directory base path
files_dir = os.path.join(os.path.dirname(__file__), '..', 'files')

# Query BQ to get distinct player links
bq_client = bigquery.Client(os.getenv('GCP_PROJECT_NAME', 'football-scrape'))
query = "SELECT player_Link " \
        "FROM `football-scrape.footballDataset.player_fantasy_year` " \
        "GROUP BY player_Link " \
        "ORDER BY player_Link " \

bq_query = bq_client.query(query, location='US')
player_links = bq_query.to_dataframe().values

data_frames = []

# iterate through team links
for row in player_links:
    player_link = row[0]

    if '.htm' in player_link:
        player_gamelog_util = PlayerGamelogUtil(player_link)

        data_frames.append(player_gamelog_util.get_gamelog_stats())

        gc.collect()

        print('Player processed for: {}. CPU%: {}. Memory: {}'.format(player_link, psutil.cpu_percent(),
                                                                          dict(psutil.virtual_memory()._asdict())))

write_to_file(pd.concat(data_frames, axis=0, sort=True))

print('All player game-logs written')
