#!/usr/bin/python
import csv
import os
from bs4 import BeautifulSoup
from TableParser import TableParser
from BrowserUtil import BrowserUtil
from FileUtil import FileUtil


def parse_html():
    browser_util = BrowserUtil()
    browser = browser_util.get_browser()
    browser.set_page_load_timeout(45)

    browser.get(url)
    inner_html = browser.execute_script("return document.body.innerHTML")

    write_page_html(inner_html)

    # Parse the page with BeautifulSoup
    return BeautifulSoup(inner_html, 'html.parser')


# write the html to file for easier work later
def write_page_html(page_html):
    html_file_name = os.path.join(dir_name, '..', path, 'fantasy_' + str(year) + '.html')

    f = open(html_file_name, 'w')
    f.write(page_html)
    f.close()

    print(html_file_name)

    if bool(os.getenv('FANTASY_DATA_BUCKET', True)):
        FileUtil().upload_to_bucket('fantasy_' + str(year) + '.html', html_file_name,
                                    os.getenv('FANTASY_HTML_BUCKET', 'fantasy-year-html'))

        os.remove(html_file_name)


def write_stat_headers(header_data):
    # Start a new file and write headers to the file
    with open(stats_file_name, 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(header_data)
    writeFile.close()


def write_stats(table_data):
    with open(stats_file_name, 'a') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(table_data)
    writeFile.close()


# Constants
table_id = 'fantasy'  # Id of the table to be parsed
base_url = 'https://www.pro-football-reference.com/years/{}/fantasy.htm'  # base url of years to iterate
dir_name = os.path.dirname(__file__)  # project directory base path
path = r"files"  # directory within the project to write file output
stats_file_name = os.path.join(dir_name, '..', path, table_id + '_year' + '.csv')

default_stat_links = [2, 3]

write_headers = True

# Loop from 1992 to 2018 (We don't have targets before 1992)
for year in range(int(os.getenv('START_YEAR', 1992)), int(os.getenv('END_YEAR', 1993))):
    url = base_url.format(year)

    # parse the html page
    soup = parse_html()

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

FileUtil().upload_to_bucket('fantasy_year_stats.csv', stats_file_name,
                            os.getenv('FANTASY_DATA_BUCKET', 'fantasy-year-data'))

if "RUNNING_IN_CONTAINER" in os.environ:
    os.remove(stats_file_name)
