#!/usr/bin/python
import os
import gc
import pandas as pd
import numpy
import psutil
import time

from multiprocessing.dummy import Pool as ThreadPool
from google.cloud import bigquery  # Imports the Google Cloud client library
from PlayerGamelogUtil import PlayerGamelogUtil
from FileUtil import FileUtil


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
files_dir = os.path.join(os.path.dirname(__file__), '../..', 'files')
GAMELOG_STATS_FILENAME = 'player_gamelog_stats_{}.csv'.format(os.getenv('GAME_LOG_CHUNK', 0))


# Query BQ to get distinct player links
bq_client = bigquery.Client(os.getenv('GCP_PROJECT_NAME', 'football-scrape'))
query = "SELECT player_Link " \
        "FROM `football-scrape.footballDataset.player_fantasy_year` " \
        "GROUP BY player_Link " \
        "ORDER BY player_Link " \

bq_query = bq_client.query(query, location='US')
player_links = bq_query.to_dataframe().values

player_links = numpy.array_split(numpy.array(player_links), 3)[int(os.getenv('GAME_LOG_CHUNK', 0))]

data_frames = []

pool = ThreadPool()

results = pool.map(crawl, player_links)

pool.close()
pool.join()

write_to_file(pd.concat(data_frames, axis=0, sort=True))

FileUtil().upload_to_bucket(GAMELOG_STATS_FILENAME, os.path.join(files_dir, GAMELOG_STATS_FILENAME),
                            os.getenv('FANTASY_DATA_BUCKET', 'fantasy-year-data'))

print('All player game-logs written')
