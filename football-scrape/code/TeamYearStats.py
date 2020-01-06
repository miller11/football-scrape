#!/usr/bin/python
import os
import re
import pandas as pd
from google.cloud import bigquery  # Imports the Google Cloud client library
from BrowserUtil import BrowserUtil


def get_record_df():
    result = soup.find('strong', text=re.compile('Record:'))  # get record paragraph
    record = result.next_element.next_element.split(',')[0]  # get the actual record (e.g. 5-10-1)
    record = record.split('-')  # split into wins losses and ties (if exist)

    if len(record) != 3:
        record.append('0')  # add ties if the record doesn't have any

    return {'wins': record[0], 'losses': record[1], 'ties': record[2]}


def get_coach_df():
    result = soup.find('strong', text=re.compile('Coach:'))  # get coach paragraph

    return {'coach_name': result.find_next().text, 'coach_link': result.find_next()['href']}


def get_points_for_df():
    result = soup.find('strong', text=re.compile('Points For:')).next_element.next_element  # get points for paragraph
    pieces = result.split(' ')  # split into parts based on spaces

    return {'points_for': pieces[1], 'points_per_game': re.sub('[^\d.]+', '', pieces[2]),
             'points_for_rank': re.sub('[^0-9]', '', pieces[3])}


def get_points_against_df():
    result = soup.find('strong', text=re.compile('Points Against:')).next_element.next_element
    pieces = result.split(' ')  # split into parts based on spaces

    return {'points_against': pieces[1], 'points_against_per_game': re.sub('[^\d.]+', '', pieces[2]),
             'points_against_rank': re.sub('[^0-9]', '', pieces[3])}


def get_def_coach_df():
    result = soup.find('strong', text=re.compile('Defensive Coordinator:'))

    if result is not None:
        return {'def_coach_name': result.find_next().text, 'def_coach_link': result.find_next()['href']}
    else:
        return {}


def get_off_coach_df():
    result = soup.find('strong', text=re.compile('Offensive Coordinator:'))

    if result is not None:
        return {'def_coach_name': result.find_next().text, 'def_coach_link': result.find_next()['href']}
    else:
        return {}


# Constants
base_url = 'https://www.pro-football-reference.com'  # base url of years to iterate
dir_name = os.path.dirname(__file__)  # project directory base path
files_dir = os.path.join(os.path.dirname(__file__), '..', 'files')

# Query BQ to get distinct team links
# bq_client = bigquery.Client(os.getenv('GCP_PROJECT_NAME', 'football-scrape'))
# query = "SELECT team_Link FROM `football-scrape.footballDataset.player_fantasy_year`" \
#         " group by team_Link order by team_Link"
# bq_query = bq_client.query(query, location='US')
# team_links_df = bq_query.to_dataframe()


# iterate through team links
# for index, row in team_links_df.iterrows():
#     team_link = row['team_Link']

team_link = '/teams/crd/2019.htm'

# build file name (e.g. 'team_crd_2019.htm')
url_pieces = team_link.split("/")
file_name = 'team_{}_{}'.format(url_pieces[2], url_pieces[3])

# parse the html page
browser_util = BrowserUtil()
soup = browser_util.parse_html(base_url + team_link, file_name)


data_frames = {}

data_frames.update(get_def_coach_df())
data_frames.update(get_coach_df())
data_frames.update(get_points_for_df())
data_frames.update(get_points_against_df())
data_frames.update(get_def_coach_df())
data_frames.update(get_off_coach_df())


print(pd.DataFrame(data_frames, index=[0]))

print('Team stats processed for: {}'.format(team_link))


