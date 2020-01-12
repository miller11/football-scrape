import os
import psutil
import re
import gc
import pandas as pd
from BrowserUtil import BrowserUtil
from FileUtil import FileUtil
from TableParser import TableParser


class TeamYearUtil:
    def __init__(self, team_link):
        # Constants
        self.base_url = 'https://www.pro-football-reference.com'  # base url of years to iterate
        self.dir_name = os.path.dirname(__file__)  # project directory base path
        self.files_dir = os.path.join(os.path.dirname(__file__), '..', 'files')

        # build file name (e.g. 'team_crd_2019.htm')
        url_pieces = team_link.split("/")
        self.html_file_name = 'team_{}_{}'.format(url_pieces[2], url_pieces[3])
        self.csv_file_name = 'team_{}_{}'.format(url_pieces[2], url_pieces[3]).replace('.htm', '.csv')

        # parse the html page
        browser_util = BrowserUtil()
        self.soup = browser_util.parse_html(self.base_url + team_link, self.html_file_name)
        self.team_link = team_link

        del browser_util

    def write_to_file(self, df):
        df.to_csv(os.path.join(self.files_dir, self.csv_file_name), index=False, encoding='utf-8')
        del df

        FileUtil().upload_to_bucket(self.csv_file_name, os.path.join(self.files_dir, self.csv_file_name),
                                    os.getenv('TEAM_YEAR_BUCKET', 'team-year-data'))

        print('File uploaded to bucket')

        if "RUNNING_IN_CONTAINER" in os.environ:
            os.remove(os.path.join(self.files_dir, self.csv_file_name))

        return True

    def get_record(self):
        result = self.soup.find('strong', text=re.compile('Record:'))  # get record paragraph
        record = result.next_element.next_element.split(',')[0]  # get the actual record (e.g. 5-10-1)
        record = record.split('-')  # split into wins losses and ties (if exist)

        if len(record) != 3:
            record.append('0')  # add ties if the record doesn't have any

        return {'wins': str(record[0]).strip(), 'losses': str(record[1]).strip(), 'ties': str(record[2]).strip()}

    def get_coach(self):
        result = self.soup.find('strong', text=re.compile('Coach:'))  # get coach paragraph

        return {'coach_name': str(result.find_next().text), 'coach_link': str(result.find_next()['href'])}

    def get_points_for(self):
        result = self.soup.find('strong',
                           text=re.compile('Points For:')).next_element.next_element  # get points for paragraph
        pieces = result.split(' ')  # split into parts based on spaces

        return {'points_for': pieces[1], 'points_per_game': re.sub('[^\d.]+', '', pieces[2]),
                'points_for_rank': re.sub('[^0-9]', '', pieces[3])}

    def get_points_against(self):
        result = self.soup.find('strong', text=re.compile('Points Against:')).next_element.next_element
        pieces = result.split(' ')  # split into parts based on spaces

        return {'points_against': pieces[1], 'points_against_per_game': re.sub('[^\d.]+', '', pieces[2]),
                'points_against_rank': re.sub('[^0-9]', '', pieces[3])}

    def get_def_coach(self):
        result = self.soup.find('strong', text=re.compile('Defensive Coordinator:'))

        if result is not None:
            return {'def_coach_name': result.find_next().text, 'def_coach_link': result.find_next()['href']}
        else:
            return {}

    def get_off_coach(self):
        result = self.soup.find('strong', text=re.compile('Offensive Coordinator:'))

        if result is not None:
            return {'off_coach_name': result.find_next().text, 'off_coach_link': result.find_next()['href']}
        else:
            return {}

    def get_team_stats(self):
        # parse the team stats table
        table_parser = TableParser(self.soup, 'team_stats')

        headers = table_parser.parse_headers([], use_aria_label_label=True)  # get all headers snake case from aria
        table_data = table_parser.parse_stats([])

        data_dict = {}

        i = 1

        while i < len(headers):
            data_dict.update({headers[i]: table_data[0][i]})
            data_dict.update({'opp_' + headers[i]: table_data[1][i]})

            i += 1

        del table_parser

        return data_dict

    def write_file(self):
        gc.collect()
        # team_link = '/teams/crd/2019.htm'

        data = {'team_link': self.team_link}

        # Get the heading data4
        data.update(self.get_record())
        data.update(self.get_coach())
        data.update(self.get_points_for())
        data.update(self.get_points_against())
        data.update(self.get_def_coach())
        data.update(self.get_off_coach())

        # Get the team stats data from the table
        data.update(self.get_team_stats())

        # close tree for soup
        self.soup.decompose()
        del self.soup

        # Write to file and capture that headers were written
        self.write_to_file(pd.DataFrame(data, index=[0]))

        gc.collect()

        print('Team stats processed for: {}. CPU%: {}. Memory: {}'.format(self.team_link, psutil.cpu_percent(),
                                                                          dict(psutil.virtual_memory()._asdict())))
