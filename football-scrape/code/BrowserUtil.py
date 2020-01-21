import os
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from FileUtil import FileUtil


class BrowserUtil:
    def __init__(self):
        self.chromedriver_path = os.environ['CHROMEDRIVER_PATH']

        if "RUNNING_IN_CONTAINER" in os.environ:
            self.headless_browser = True
        else:
            self.headless_browser = False

    # write the html to file for easier work later
    @staticmethod
    def write_page_html(page_html, html_file_name):
        f = open(html_file_name, 'w')
        f.write(page_html)
        f.close()

        print(html_file_name)

        if bool(os.getenv('SAVE_HTML', True)):
            FileUtil().upload_to_bucket(html_file_name, html_file_name,
                                        os.getenv('HTML_BUCKET', 'pfr-html-files'))

            os.remove(html_file_name)

    @staticmethod
    def use_cached_file(html_file_name):
        return os.getenv('USE_CACHED_FILES', False) and FileUtil().check_file_exists(html_file_name,
                                                                                     os.getenv('HTML_BUCKET',
                                                                                               'pfr-html-files'))

    def parse_html(self, url, html_file_name):
        if self.use_cached_file(html_file_name):
            print('Using cached file: ' + html_file_name)
            FileUtil().download_file(html_file_name, html_file_name, os.getenv('HTML_BUCKET', 'pfr-html-files'))

            soup = BeautifulSoup(open(html_file_name), "html.parser")
            os.remove(html_file_name)

            return soup

        try:
            browser_util = BrowserUtil()
            browser = browser_util.get_browser()
            browser.set_page_load_timeout(45)

            browser.get(url)
            inner_html = browser.execute_script("return document.body.innerHTML")
            browser.close()

        except TimeoutException:
            browser_util = BrowserUtil()
            browser = browser_util.get_browser()
            browser.set_page_load_timeout(45)

            browser.get(url)
            inner_html = browser.execute_script("return document.body.innerHTML")
            browser.close()

        self.write_page_html(inner_html, html_file_name)

        # Parse the page with BeautifulSoup
        return BeautifulSoup(inner_html, 'html.parser')

    def get_browser(self):
        # get headless chrome driver and get inner html
        if self.headless_browser:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
        else:
            options = Options()
            options.headless = True

        return webdriver.Chrome(options=options, executable_path=self.chromedriver_path)
