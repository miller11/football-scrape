import re


class TableParser:
    def __init__(self, soup, table_id):
        self.soup = soup
        self.table_id = table_id

    def parse_headers(self, stat_links, additional_headers=None):
        if self.soup.find('table', attrs={'id': self.table_id}):

            # Get the table header
            header_rows = self.soup.find('table', attrs={'id': self.table_id}).find('thead')
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

            return cols

    def parse_stats(self, stat_links, additional_data=None):
        if self.soup.find('table', attrs={'id': self.table_id}):

            # Pull out the passing table body
            table_body_rows = self.soup.find('table', attrs={'id': self.table_id}).find('tbody').find_all('tr')
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

            return table_data
