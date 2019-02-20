#!/usr/bin/python
import csv
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re


def write_stat_headers(stat_name, stat_header_written):
    if soup.find('table', attrs={'id': stat_name}) and not stat_header_written:

        header_rows = soup.find('table', attrs={'id': stat_name}).find('thead')
        header_rows = header_rows.find_all('tr', attrs={'class': None})

        cols = header_rows[0].find_all('th')
        cols = [ele.text.strip().encode('utf-8') for ele in cols]
        cols.insert(0, 'Year')
        cols.insert(1, 'Year Link')
        cols.insert(5, 'Tm Link')  # Add team link header column

        # Start a new file and write headers to the file
        with open(os.path.join(dirname, path, 'stats',  stat_name + '.csv'), 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerow(cols)
        writeFile.close()

        return True
    else:
        return stat_header_written


def write_stats(stat_name):
    if soup.find('table', attrs={'id': stat_name}):

        # Pull out the passing table body
        passing_body_rows = soup.find('table', attrs={'id': stat_name}).find('tbody').find_all('tr', attrs={'class': 'full_table'})
        passing_data = []  # Var to hold all the passing data before we write it to a file

        for passing_row in passing_body_rows:
            cols = passing_row.find_all('th')
            year = re.sub(r"\D", "", cols[0].text.strip())  # Get year, removing special characters

            cols = passing_row.find_all('td')

            if cols[1].find('a'):
                team_link = cols[1].find('a')['href']  # Team Link from the team link column
            else:
                team_link = 'none'

            cols = [ele.text.strip() for ele in cols]

            cols.insert(0, player[0])
            cols.insert(1, player[1])
            cols.insert(2, year)
            cols.insert(5, team_link)  # Add team link
            passing_data.append(cols)

        with open(os.path.join(dirname, path, 'stats', stat_name + '.csv'), 'a') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(passing_data)
        writeFile.close()


def get_players():
    players_temp = []

    with open(os.path.join(dirname, path, 'playerList.csv'), 'r') as readFile:
        reader = csv.reader(readFile)
        next(reader)  # Skip header row
        for row in reader:
            players_temp.append(row)
    readFile.close()

    return players_temp


# Pull in player file
dirname = os.path.dirname(__file__)
path = r"files"

# Make array of the player name and link
players = get_players()

# Keep track of if the headers have been written for each file
passing_headers = False
running_headers = False
defense_headers = False
scoring_headers = False


baseUrl = 'https://www.pro-football-reference.com'

for player in players:
    options = Options()
    options.headless = True

    browser = webdriver.Chrome(executable_path='/Users/rhmiller/notebooks/football-scrape/webdriver/chromedriver',
                               options=options)
    browser.get(baseUrl + player[1])
    innerHTML = browser.execute_script("return document.body.innerHTML")

    # Parse the page
    soup = BeautifulSoup(innerHTML, 'html.parser')

    # Deal with passing
    passing_headers = write_stat_headers('passing', passing_headers)
    write_stats('passing')

    # Deal with rushing & receiving
    running_headers = write_stat_headers('rushing_and_receiving', running_headers)
    write_stats('rushing_and_receiving')

    # Deal with defense
    defense_headers = write_stat_headers('defense', defense_headers)
    write_stats('defense')

    # Deal with scoring table
    scoring_headers = write_stat_headers('scoring', scoring_headers)
    write_stats('scoring')

    browser.close()
    print('player ' + player[0] + ' complete')

print('Complete')
