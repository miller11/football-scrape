#!/usr/bin/python
import os

# Imports the Google Cloud client library
from google.cloud import bigquery

# Constants
base_url = 'https://www.pro-football-reference.com'  # base url of years to iterate
dir_name = os.path.dirname(__file__)  # project directory base path
path = r"files"  # directory within the project to write file output
stats_file_name = os.path.join(dir_name, '..', path, 'team' + '_year' + '.csv')


# Query BQ to get distinct team links
bq_client = bigquery.Client(os.getenv('GCP_PROJECT_NAME', 'football-scrape'))
query = "SELECT team_Link FROM `football-scrape.footballDataset.player_fantasy_year`" \
        " group by team_Link order by team_Link"
bq_query = bq_client.query(query, location='US')
team_links_df = bq_query.to_dataframe()


# iterate through team links
for index, row in team_links_df.iterrows():
    team_link = row['team_Link']


