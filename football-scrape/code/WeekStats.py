#!/usr/bin/python
import csv
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from TableParser import TableParser
import pandas as pd


# helper method to get all the players out of the specified file and build and a 2D array of [year, player_link]
def get_players():
    players_temp = []

    with open(os.path.join(dir_name, '..', path, 'stats', 'fantasy.csv'), 'r') as readFile:
        reader = csv.reader(readFile)
        next(reader)  # Skip header row
        for row in reader:
            players_temp.append([row[0], row[34]])  # get the link for the player (year, player_link)
    readFile.close()

    return players_temp


# helper method to build the link to the player gamelog based on the player id out of the file built by FFLYearStats.py
def build_gamelog_link(player_link):
    return '{}/gamelog/{}/'.format(player_link.replace('.htm', ''), year)


def write_page_html(page_html, player_link):
    player_link = player_link.replace('/', '').replace('.htm', '')

    # Start a new file and write headers to the file
    html_file_name = os.path.join(dir_name, '..', path, 'pages', 'playerStats', player_link + str(year) + '.html')

    f = open(html_file_name, 'w')
    f.write(page_html)
    f.close()


# simple method to output the pandas dataframe to csv in the stats folder
def write_file(data_frame, file_year):
    # Start a new file and write data frame to the file
    data_frame.to_csv(os.path.join(dir_name, '..', path, 'stats', 'weekly_stats_' + file_year.__str__() + '.csv'),
                      encoding='utf-8')


# Constants
base_url = 'https://www.pro-football-reference.com'  # base url of years to iterate
dir_name = os.path.dirname(__file__)  # project directory base path
path = r"files"  # directory within the project to write file output
table_id = "stats"  # table that we are after on the page

default_stat_links = [5]

cur_year = -1

# !!!!! Start of program !!!!!

# get all the players from the fantasy file
players = get_players()

data_frames = []

# loop through all players fetched from the get_players() method
for player in players:
    year = int(player[0])

    #  if its the first player, set the year
    if cur_year == -1:
        cur_year = year
    elif cur_year != year:  # if the year has changed write the file
        write_file(pd.concat(data_frames, axis=0, sort=True), cur_year)  # concat the data frames and write
        print("Stats written for year: {}".format(cur_year))
        data_frames = []
        cur_year = year

    # use headless chrome browser to pull down the table
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')

    browser = webdriver.Chrome(options=options, executable_path="/usr/bin/chromedriver")

    browser.get(base_url + build_gamelog_link(player[1]))
    innerHTML = browser.execute_script("return document.body.innerHTML")
    write_page_html(innerHTML, player[1])

    browser.close()

    # Parse the page
    soup = BeautifulSoup(innerHTML, 'html.parser')

    # instantiate the table parser
    tableParser = TableParser(soup, table_id)

    # get the table headers
    headers = tableParser.parse_headers(default_stat_links, additional_headers=['Year'], use_data_stat_label=True)

    # get the table data
    data = tableParser.parse_stats(default_stat_links, additional_data=[player[0]])
    print('Stats fetched for: {} ({})'.format(player[1], player[0]))

    # add the data frame to the year's worth of data frames
    data_frames.append(pd.DataFrame(data, columns=headers))

# once we are out of players write the last year
write_file(pd.concat(data_frames, axis=0, sort=True), cur_year)
