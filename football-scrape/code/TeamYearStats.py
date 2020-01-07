#!/usr/bin/python
import os
import re
import pandas as pd
from google.cloud import bigquery  # Imports the Google Cloud client library
from BrowserUtil import BrowserUtil
from TableParser import TableParser
from FileUtil import FileUtil


def get_record():
    result = soup.find('strong', text=re.compile('Record:'))  # get record paragraph
    record = result.next_element.next_element.split(',')[0]  # get the actual record (e.g. 5-10-1)
    record = record.split('-')  # split into wins losses and ties (if exist)

    if len(record) != 3:
        record.append('0')  # add ties if the record doesn't have any

    return {'wins': record[0].strip(), 'losses': record[1].strip(), 'ties': record[2].strip()}


def get_coach():
    result = soup.find('strong', text=re.compile('Coach:'))  # get coach paragraph

    return {'coach_name': result.find_next().text, 'coach_link': result.find_next()['href']}


def get_points_for():
    result = soup.find('strong', text=re.compile('Points For:')).next_element.next_element  # get points for paragraph
    pieces = result.split(' ')  # split into parts based on spaces

    return {'points_for': pieces[1], 'points_per_game': re.sub('[^\d.]+', '', pieces[2]),
            'points_for_rank': re.sub('[^0-9]', '', pieces[3])}


def get_points_against():
    result = soup.find('strong', text=re.compile('Points Against:')).next_element.next_element
    pieces = result.split(' ')  # split into parts based on spaces

    return {'points_against': pieces[1], 'points_against_per_game': re.sub('[^\d.]+', '', pieces[2]),
            'points_against_rank': re.sub('[^0-9]', '', pieces[3])}


def get_def_coach():
    result = soup.find('strong', text=re.compile('Defensive Coordinator:'))

    if result is not None:
        return {'def_coach_name': result.find_next().text, 'def_coach_link': result.find_next()['href']}
    else:
        return {}


def get_off_coach():
    result = soup.find('strong', text=re.compile('Offensive Coordinator:'))

    if result is not None:
        return {'def_coach_name': result.find_next().text, 'def_coach_link': result.find_next()['href']}
    else:
        return {}


def get_team_stats():
    # parse the team stats table
    table_parser = TableParser(soup, 'team_stats')

    headers = table_parser.parse_headers([], use_aria_label_label=True)  # get all headers snake case from aria
    table_data = table_parser.parse_stats([])

    data_dict = {}

    i = 1

    while i < len(headers):
        data_dict.update({headers[i]: table_data[0][i]})
        data_dict.update({'opp_' + headers[i]: table_data[1][i]})

        i += 1

    return data_dict


# Constants
base_url = 'https://www.pro-football-reference.com'  # base url of years to iterate
dir_name = os.path.dirname(__file__)  # project directory base path
files_dir = os.path.join(os.path.dirname(__file__), '..', 'files')

# Query BQ to get distinct team links
bq_client = bigquery.Client(os.getenv('GCP_PROJECT_NAME', 'football-scrape'))
query = "SELECT team_Link FROM `football-scrape.footballDataset.player_fantasy_year`" \
        " group by team_Link order by team_Link"
bq_query = bq_client.query(query, location='US')
team_links_df = bq_query.to_dataframe()


data_frames = []

# iterate through team links
for index, row in team_links_df.iterrows():
    team_link = row['team_Link']

    # team_link = '/teams/crd/2019.htm'

    # build file name (e.g. 'team_crd_2019.htm')
    url_pieces = team_link.split("/")
    file_name = 'team_{}_{}'.format(url_pieces[2], url_pieces[3])

    # parse the html page
    browser_util = BrowserUtil()
    soup = browser_util.parse_html(base_url + team_link, file_name)

    data = {'team_link': team_link}

    # Get the heading data
    data.update(get_record())
    data.update(get_coach())
    data.update(get_points_for())
    data.update(get_points_against())
    data.update(get_def_coach())
    data.update(get_off_coach())

    # Get the team stats data from the table
    data.update(get_team_stats())

    data_frames.append(pd.DataFrame(data, index=[0]))

    print('Team stats processed for: {}'.format(team_link))

complete_df = pd.concat(data_frames, axis=0, sort=True)

complete_df.to_csv(os.path.join(files_dir, 'team_year_stats.csv'), index=False, encoding='utf-8')

print('File written')

FileUtil().upload_to_bucket('team_year_stats.csv', os.path.join(files_dir, 'team_year_stats.csv'),
                            os.getenv('FANTASY_DATA_BUCKET', 'fantasy-year-data'))

print('File uploaded to bucket')

if "RUNNING_IN_CONTAINER" in os.environ:
    os.remove(os.path.join(files_dir, 'team_year_stats.csv'))
