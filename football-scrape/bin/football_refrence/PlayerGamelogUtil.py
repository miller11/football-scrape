import gc
import pandas as pd
from BrowserUtil import BrowserUtil
from TableParser import TableParser


class PlayerGamelogUtil:
    def __init__(self, player_link):
        # Constants
        self.base_url = 'https://www.pro-football-reference.com'  # base url of years to iterate

        # build file name (e.g. 'team_crd_2019.htm')
        url_pieces = player_link.split("/")
        self.html_file_name = 'player_gamelog_{}'.format(url_pieces[3])

        # parse the html page
        browser_util = BrowserUtil()
        gamelog_url = '{}/players/{}/{}/gamelog'.format(self.base_url, url_pieces[2], url_pieces[3])

        self.soup = browser_util.parse_html(gamelog_url, self.html_file_name)
        self.player_link = player_link

        del browser_util

    def get_gamelog_stats(self):
        gc.collect()

        # Get the team stats data from the table
        default_stat_links = [7, 9, 10]

        table_parser = TableParser(self.soup, 'stats')

        # parse headers including headers for team_link and game_link and player_link as the additional header
        headers = table_parser.parse_headers(default_stat_links, additional_headers=['player_link'])

        # parse data including getting the link for the team and game
        data = table_parser.parse_stats(default_stat_links, additional_data=[self.player_link])

        # close tree for soup
        self.soup.decompose()
        del self.soup

        # Write to file and capture that headers were written
        return pd.DataFrame(data, columns=headers)
