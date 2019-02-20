#!/usr/bin/python

import csv
import os.path
import requests
from bs4 import BeautifulSoup
import re


def write_passing_headers():
    header_rows = soup.find('table', attrs={'id': 'passing'}).find('thead')
    header_rows = header_rows.find_all('tr', attrs={'class': None})

    cols = header_rows[0].find_all('th')
    cols = [ele.text.strip().encode('utf-8') for ele in cols]
    cols.insert(0, 'Player')
    cols.insert(1, 'Player Link')
    cols.insert(5, 'Tm Link')  # Add team link header column

    # Start a new file and write headers to the file
    with open(os.path.join(dirname, path, 'stats',  'passing.csv'), 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(cols)
    writeFile.close()

    global passing_headers
    passing_headers = True


def passing_stats():
    if soup.find('table', attrs={'id': 'passing'}):
        global passing_headers

        if not passing_headers:
            write_passing_headers()

        # Pull out the passing table body
        passing_body_rows = soup.find('table', attrs={'id': 'passing'}).find('tbody').find_all('tr', attrs={'class': 'full_table'})
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

        with open(os.path.join(dirname, path, 'stats', 'passing.csv'), 'a') as writeFile:
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

baseUrl = 'https://www.pro-football-reference.com'

for player in players:
    r = requests.get(baseUrl + player[1])

    # Parse the page
    soup = BeautifulSoup(r.text, 'html.parser')

    passing_stats()
    print('player ' + player[0] + ' complete')

print('Complete')
