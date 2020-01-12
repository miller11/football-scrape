#!/usr/bin/python
import os
import gc
from pympler.tracker import SummaryTracker
from google.cloud import bigquery  # Imports the Google Cloud client library
from TeamYearUtil import TeamYearUtil

# Query BQ to get distinct team links
bq_client = bigquery.Client(os.getenv('GCP_PROJECT_NAME', 'football-scrape'))
query = "SELECT team_Link FROM `football-scrape.footballDataset.player_fantasy_year`" \
        " GROUP BY team_Link ORDER BY team_Link DESC"
bq_query = bq_client.query(query, location='US')
team_links = bq_query.to_dataframe().values


tracker = SummaryTracker()

# iterate through team links
for row in team_links:
    if '.htm' in row[0]:
        team_year_util = TeamYearUtil(row[0])
        team_year_util.write_file()

        gc.collect()

tracker.print_diff()

print('All teams written')


