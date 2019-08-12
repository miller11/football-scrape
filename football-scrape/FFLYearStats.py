#!/usr/bin/python
import csv
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re


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


def write_stat_headers(stat_links, additional_headers=None):
    if soup.find('table', attrs={'id': table_id}):

        # Get the table header
        header_rows = soup.find('table', attrs={'id': table_id}).find('thead')
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
        with open(os.path.join(dir_name, path, 'stats', table_id + '.csv'), 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerow(cols)
        writeFile.close()


def write_stats(stat_links, additional_data=None):
    if soup.find('table', attrs={'id': table_id}):

        # Pull out the passing table body
        table_body_rows = soup.find('table', attrs={'id': table_id}).find('tbody').find_all('tr')
        table_data = []  # Var to hold all the passing data before we write it to a file

        for table_row in table_body_rows:
            # Deal with header column in the row
            cols = table_row.find_all('th')
            first_column = re.sub(r"\*", "", cols[0].text.strip())  # Get column header strip *
            first_column_link = first_column

            if cols[0].find('a'):
                first_column_link = cols[0].find('a')['href']

            # Get the rest of the columns in the row
            cols = table_row.find_all('td')

            if len(cols):
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
                    elif cols[stat_link - 2].find('a'):
                        data.append(cols[stat_link - 2].find('a')['href'])  # Team Link from the team link column
                    else:
                        data.append(cols[stat_link - 2].text.strip())

                # Add composed columns to list
                table_data.append(data)

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
for year in range(1970, 2019):
    url = base_url.format(year)

    # parse the html page
    soup = parse_html()

    # write the table headers
    if write_headers:
        write_stat_headers(default_stat_links, additional_headers=['Year'])
        write_headers = False
        print('Headers written')

    # get the table data
    write_stats(default_stat_links, additional_data=[year])
    print('Stats written for year: {}'.format(year))
