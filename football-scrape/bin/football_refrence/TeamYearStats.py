#!/usr/bin/python
import os
import gc
import pandas as pd
import psutil
import time
from pympler.tracker import SummaryTracker
from google.cloud import bigquery  # Imports the Google Cloud client library
from TeamYearUtil import TeamYearUtil
from FileUtil import FileUtil

YEAR_STATS_CSV = 'team_year_stats.csv'


def write_to_file(df):
    df.to_csv(os.path.join(files_dir, YEAR_STATS_CSV), index=False, encoding='utf-8')
    return True


# constants
dir_name = os.path.dirname(__file__)  # project directory base path
files_dir = os.path.join(os.path.dirname(__file__), '../..', 'files')

# Query BQ to get distinct team links
bq_client = bigquery.Client(os.getenv('GCP_PROJECT_NAME', 'football-scrape'))
query = "SELECT team_Link FROM `football-scrape.footballDataset.player_fantasy_year`" \
        " GROUP BY team_Link ORDER BY team_Link DESC "
bq_query = bq_client.query(query, location='US')
team_links = bq_query.to_dataframe().values

tracker = SummaryTracker()

data_frames = []

# iterate through team links
for row in team_links:
    if '.htm' in row[0]:
        team_year_util = TeamYearUtil(row[0])
        team_df = team_year_util.get_team_year_stats()

        data_frames.append(team_df)

        print('Team stats processed for: {}. CPU%: {}. Memory: {}'.format(row[0], psutil.cpu_percent(),
                                                                          dict(psutil.virtual_memory()._asdict())))

        gc.collect()
        time.sleep(1)

# concat dataframes and write to file
write_to_file(pd.concat(data_frames, axis=0, sort=True))

tracker.print_diff()

print('All teams written')

FileUtil().upload_to_bucket(YEAR_STATS_CSV, os.path.join(files_dir, YEAR_STATS_CSV),
                            os.getenv('FANTASY_DATA_BUCKET', 'fantasy-year-data'))

print('File uploaded to bucket')

if "RUNNING_IN_CONTAINER" in os.environ:
    os.remove(os.path.join(files_dir, YEAR_STATS_CSV))

print('All teams written')

