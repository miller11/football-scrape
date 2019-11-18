import os
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


class BrowserUtil:
    def __init__(self):
        self.chromedriver_path = os.environ['CHROMEDRIVER_PATH']

        if "USE_HEADLESS_BROWSER" in os.environ:
            self.headless_browser = True

    def get_browser(self):
        # get headless chrome driver and get inner html

        if self.headless_browser:
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        else:
            options = Options()
            options.headless = True

        return webdriver.Chrome(options=options, executable_path=self.chromedriver_path)
