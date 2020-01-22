#!/usr/bin/python
import os
import gc
import pandas as pd
import psutil
import time

from queue import Queue
from threading import Thread

from multiprocessing.dummy import Pool as ThreadPool
from google.cloud import bigquery  # Imports the Google Cloud client library
from PlayerGamelogUtil import PlayerGamelogUtil


def write_to_file(df):
    df.to_csv(os.path.join(files_dir, GAMELOG_STATS_FILENAME), index=False, encoding='utf-8')
    del df


def crawl(data):
    player_link = data[0]

    if '.htm' in player_link:
        player_gamelog_util = PlayerGamelogUtil(player_link)

        data_frames.append(player_gamelog_util.get_gamelog_stats())

        gc.collect()

        print('Player processed for: {}. CPU%: {}. Memory: {}'.format(player_link, psutil.cpu_percent(),
                                                                      dict(psutil.virtual_memory()._asdict())))

        time.sleep(1)

    return True


# constants
dir_name = os.path.dirname(__file__)  # project directory base path
files_dir = os.path.join(os.path.dirname(__file__), '..', 'files')
GAMELOG_STATS_FILENAME = 'player_gamelog_stats_{}.csv'.format(os.getenv('START_YEAR', 1992))


# Query BQ to get distinct player links
bq_client = bigquery.Client(os.getenv('GCP_PROJECT_NAME', 'football-scrape'))
query_params = [
    bigquery.ScalarQueryParameter('start_year', 'INTEGER', os.getenv('START_YEAR', 1992))
]
job_config = bigquery.QueryJobConfig()
job_config.query_parameters = query_params
query = "SELECT player_Link " \
        "FROM `football-scrape.footballDataset.player_fantasy_year` " \
        "WHERE Year >= @start_year " \
        "GROUP BY player_Link " \
        "ORDER BY player_Link " \

bq_query = bq_client.query(query, job_config=job_config, location='US')
player_links = bq_query.to_dataframe().values

data_frames = []

pool = ThreadPool()

results = pool.map(crawl, player_links)

pool.close()
pool.join()

write_to_file(pd.concat(data_frames, axis=0, sort=True))

print('All player game-logs written')
