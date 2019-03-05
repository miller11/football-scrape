#!/usr/bin/python
import csv
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re


def write_stat_headers(stat_name, stat_header_written, stat_links, additional_headers=None):
    if soup.find('table', attrs={'id': stat_name}) and not stat_header_written:

        # Get the table header
        header_rows = soup.find('table', attrs={'id': stat_name}).find('thead')
        header_rows = header_rows.find_all('tr', attrs={'class': None})

        # Define the data object
        cols = []

        # Prepend the column list with player name and player link fields
        if additional_headers is not None:
            for additional_header in additional_headers:
                cols.append(additional_header)

        # Get all the header column names and strip them of whitespace
        headers = header_rows[0].find_all('th')

        for ele in headers:
            cols.append(ele.text.strip().encode('utf-8'))

        # For all the stat links get the name of the stat and append them to the header list
        for stat_link in stat_links:
            cols.append(cols[stat_link] + ' Link')

        # Start a new file and write headers to the file
        with open(os.path.join(dirname, path, 'stats', stat_name + '.csv'), 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerow(cols)
        writeFile.close()

        # Return the column headers to pass to the write_stats method
        return True
    else:
        # If the stat doesn't exist or are already written just return them again in their current state
        return stat_header_written


def write_stats(stat_name, stat_links, additional_data=None):
    if soup.find('table', attrs={'id': stat_name}):

        # Pull out the passing table body
        passing_body_rows = soup.find('table', attrs={'id': stat_name}).find('tbody').find_all('tr', attrs={
            'class': 'full_table'})
        passing_data = []  # Var to hold all the passing data before we write it to a file

        for passing_row in passing_body_rows:
            # Deal with header column in the row
            cols = passing_row.find_all('th')
            first_column = re.sub(r"\*", "", cols[0].text.strip())  # Get column header strip *
            first_column_link = first_column

            if cols[0].find('a')['href']:
                first_column_link = cols[0].find('a')['href']

            # Get the rest of the columns in the row
            cols = passing_row.find_all('td')

            data = [ele.text.strip() for ele in cols]

            # Add in the first column
            data.insert(0, first_column)

            # Prepend with additional dat matching additional headers
            if additional_data is not None:
                for idx, val in enumerate(additional_data):
                    data.insert(idx, additional_data[idx])

            # For all the stat links get the link and then append them to the list
            for stat_link in stat_links:
                if stat_link == 0:
                    data.append(first_column_link)
                elif cols[stat_link].find('a'):
                    data.append(cols[stat_link].find('a')['href'])  # Team Link from the team link column
                else:
                    data.append(cols[stat_link].text.strip())

            # Add composed columns to list
            passing_data.append(data)

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

default_stat_links = [0, 1, 5]
default_additional_headers = ['Player Name', 'Player Link']

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
    passing_headers = write_stat_headers('passing', passing_headers, default_stat_links,
                                         additional_headers=default_additional_headers)
    write_stats('passing', default_stat_links, additional_data=player)

    # Deal with rushing & receiving
    running_headers = write_stat_headers('rushing_and_receiving', running_headers, default_stat_links,
                                         additional_headers=default_additional_headers)
    write_stats('rushing_and_receiving', default_stat_links, additional_data=player)

    # Deal with defense
    defense_headers = write_stat_headers('defense', defense_headers, default_stat_links,
                                         additional_headers=default_additional_headers)
    write_stats('defense', default_stat_links, additional_data=player)

    # Deal with scoring table
    scoring_headers = write_stat_headers('scoring', scoring_headers, default_stat_links,
                                         additional_headers=default_additional_headers)
    write_stats('scoring', default_stat_links, additional_data=player)

    browser.close()
    print('player ' + player[0] + ' complete')

print('Player stats Complete')
