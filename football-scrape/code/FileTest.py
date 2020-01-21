#!/usr/bin/python
import os
from FileUtil import FileUtil
from BrowserUtil import BrowserUtil

base_url = 'https://www.pro-football-reference.com'
team_link = '/teams/crd/2019.htm'
url_pieces = team_link.split("/")
html_file_name = 'team_{}_{}'.format(url_pieces[2], url_pieces[3])


result = FileUtil().check_file_exists(html_file_name, os.getenv('HTML_BUCKET', 'pfr-html-files'))

print(result)


browser_util = BrowserUtil()
soup = browser_util.parse_html(base_url + team_link, html_file_name)

print(soup)
