#!/usr/bin/python
import csv
import os
from TableParser import TableParser
from BrowserUtil import BrowserUtil
from FileUtil import FileUtil


def write_stat_headers(header_data):
    # Start a new file and write headers to the file
    with open(os.path.join(files_dir, stats_file_name), 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(header_data)
    writeFile.close()


def write_stats(table_data):
    with open(os.path.join(files_dir, stats_file_name), 'a') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(table_data)
    writeFile.close()


# Constants
table_id = 'fantasy'  # Id of the table to be parsed
base_url = 'https://www.pro-football-reference.com/years/{}/fantasy.htm'  # base url of years to iterate
files_dir = os.path.join(os.path.dirname(__file__), '../..', 'files')
stats_file_name = table_id + '_year' + '.csv'

default_stat_links = [2, 3]

write_headers = True

# Loop from 1992 to 2018 (We don't have targets before 1992)
for year in range(int(os.getenv('START_YEAR', 1992)), int(os.getenv('END_YEAR', 1993))):
    url = base_url.format(year)

    # parse the html page
    browser_util = BrowserUtil()
    soup = browser_util.parse_html(url, str(year) + '_fantasy.htm')

    # instantiate the table parser
    tableParser = TableParser(soup, table_id)

    # write the table headers
    if write_headers:
        write_stat_headers(tableParser.parse_headers(default_stat_links, additional_headers=['Year']))
        write_headers = False
        print('Headers written')

    # get the table data
    write_stats(tableParser.parse_stats(default_stat_links, additional_data=[year]))
    print('Stats written for year: {}'.format(year))

FileUtil().upload_to_bucket('fantasy_year_stats.csv', os.path.join(files_dir, stats_file_name),
                            os.getenv('FANTASY_DATA_BUCKET', 'fantasy-year-data'))

if "RUNNING_IN_CONTAINER" in os.environ:
    os.remove(os.path.join(files_dir, stats_file_name))
