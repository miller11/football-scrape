#!/usr/bin/python
import csv
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from TableParser import TableParser


def parse_html():
    # get headless chrome driver and get inner html
    options = Options()
    options.headless = True

    browser = webdriver.Chrome(executable_path='/Users/rhmiller/notebooks/football-scrape/webdriver/chromedriver',
                               options=options)
    browser.get(url)
    inner_html = browser.execute_script("return document.body.innerHTML")

    # Parse the page with BeautifulSoup
    return BeautifulSoup(inner_html, 'html.parser')


def write_stat_headers(header_data):
    # Start a new file and write headers to the file
    with open(os.path.join(dir_name, path, 'stats', table_id + '.csv'), 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(header_data)
    writeFile.close()


def write_stats(table_data):
    with open(os.path.join(dir_name, path, 'stats', table_id + '.csv'), 'a') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(table_data)
    writeFile.close()


# Constants
table_id = 'fantasy'  # Id of the table to be parsed
base_url = 'https://www.pro-football-reference.com/years/{}/fantasy.htm'  # base url of years to iterate
dir_name = os.path.dirname(__file__)  # project directory base path
path = r"files"  # directory within the project to write file output

default_stat_links = [2, 3]

write_headers = True

# Loop from 1970 to 2018
for year in range(2018, 2019):
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
