from getpass import getpass
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class HumbleDriver:
    def __init__(self, url: str, max_auth_time: int = 30):
        self.base_url = url
        self.max_auth_time = max_auth_time

        # Initialize Selenium browser driver
        opts = ChromeOptions()
        opts.add_argument("--window-size=1600,900")

        self.driver = webdriver.Chrome(options=opts)
        self.driver.implicitly_wait(1)
        self.driver.get(url)

        self.wait = WebDriverWait(self.driver, 10)
        self.auth_wait = WebDriverWait(self.driver, self.max_auth_time)

    def __enter__(self):
        # TODO: implement context manager __enter__
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        # TODO: implement context manager __exit__
        pass

    def login(self, user: str = os.environ.get("HBGET_USER"),
              pw: str = os.environ.get("HBGET_PASS")):

        self.driver.get(self.base_url)

        # Click login button
        login_btn = self.driver.find_element(By.LINK_TEXT, "Log In")
        login_btn.click()

        # Submit login form
        form_user = self.driver.find_element(By.NAME, "username")
        if user is None:
            user = input("Please provide your HumbleBundle username: ")
        form_user.send_keys(user)

        form_pass = self.driver.find_element(By.NAME, "password")
        if pw is None:
            pw = getpass("Please provide your HumbleBundle password: ")
        form_pass.send_keys(pw)

        form_submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type=submit]")
        form_submit_btn.click()

        # Wait for authentication to complete (including MFA prompt)
        print(f"If MFA is enabled you'll need to provide the code...you have {self.max_auth_time} seconds.")
        try:
            self.auth_wait.until(EC.none_of(EC.title_contains("Log In")))
        except TimeoutException:
            print("The authentication request timed out.")
            again = input("Try again? (y/n): ")
            if again.lower() == 'y':
                self.login(user)
            else:
                sys.exit()

    def get_purchases(self) -> list:
        self.driver.get(f"{self.base_url}/home/purchases")

        # Wait for purchase rows to load
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".results .body .row")))
        purchases = self.driver.find_elements(By.CSS_SELECTOR, ".row")
        return purchases

    def get_download_links(self, filetype: str):
        # Wait for rows to load with download links
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".row")))

        # Extract download links from row elements
        download_elements = self.driver.find_elements(By.CSS_SELECTOR, ".download a[href^='https://dl.humble.com']")
        download_elements = list(filter(lambda x: x.text.strip().lower() == filetype, download_elements))
        download_links = [x.get_attribute("href") for x in download_elements]
        return download_links
    
    def get_download_links_by_title(self, filetype: str):
        # Wait for rows to load with download links
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".row")))

        # Extract download titles and hrefs from row elements
        row_elements = self.driver.find_elements(By.CSS_SELECTOR, ".row")
        download_links_by_title = {}
        for row in row_elements:
            title = row.find_element(By.CSS_SELECTOR, ".title").text.strip()
            href_elements = row.find_elements(By.CSS_SELECTOR, ".download a[href^='https://dl.humble.com']")

            # Check each download option for matching `filetype`
            for ele in href_elements:
                if ele.text.strip().lower() == filetype:
                    download_links_by_title[title] = ele.get_attribute("href")
        return download_links_by_title

    def select_purchase(self):
        purchases = self.get_purchases()
        if len(purchases) == 0:
            return

        for i, p in enumerate(purchases):
            print(f"{i:>3}: {p.text}")

        while(True):
            sel = input(f"Select one above purchases (0-{len(purchases)}): ")
            try:
                sel = int(sel)
                if sel < 0 or sel > len(purchases):
                    continue
                key = self.get_purchases()[sel].get_attribute("data-hb-gamekey")
                self.driver.get(f"{self.base_url}/downloads?key={key}")
                break
            except ValueError:
                continue





