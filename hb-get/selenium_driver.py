"""Selenium driver and utility functions for interfacing with the HumbleBundle website.

Typical usage example:

    hb = sd.HumbleDriver("https://www.humblebundle.com")
    hb.login()
    purchases = hb.get_purchases()
    hb.select_purchase()
    download_links_by_title = hb.get_download_links_by_title(args.filetype)
    for title,link in download_links_by_title.items():
        print(title, link)
"""
from getpass import getpass
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class HumbleDriver:
    """Selenium driver class"""
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

    def login(self,
              user: str = os.environ.get("HBGET_USER"),
              password: str = os.environ.get("HBGET_PASS")):
        """Authenticate user on the HumbleBundle login page.

        Note: It is recommended to provide these values via the default
            environment variables HBGET_USER and HBGET_PASS.

        Args:
            user: A string of the user's HumbleBundle username.
            password: A string of the user's HumbleBundle password.
        """
        try:
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
            if password is None:
                password = getpass("Please provide your HumbleBundle password: ")
            form_pass.send_keys(password)

            form_submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type=submit]")
            form_submit_btn.click()

            # TODO: identify 2FA screen and reply with conditional warning/log message
            # TODO: identify failed login screen and query user for another login attempt

            # Wait for authentication to complete (including MFA prompt)
            print("If MFA is enabled, you must provide the code.")
            print(f"You have {self.max_auth_time} seconds.")
            try:
                self.auth_wait.until(EC.none_of(EC.title_contains("Log In")))
            except TimeoutException:
                print("The authentication request timed out.")
                again = input("Try again? (y/n): ")
                if again.lower() == 'y':
                    self.login(user)
                else:
                    sys.exit()
        except KeyboardInterrupt:
            print("Keyboard Interrupt. Exiting...")

    def get_purchases(self) -> list:
        """Retrives a list of elements corresponding to the purchases of user.

        Returns:
            A list of type List[WebElement] of each purchase on a user's purchases page
        """

        self.driver.get(f"{self.base_url}/home/purchases")

        # Wait for purchase rows to load
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".results .body .row")))
        purchases = self.driver.find_elements(By.CSS_SELECTOR, ".row")
        return purchases

    def get_download_links(self, filetype: str):
        """Retreive a list of download links for all items in a bundle

        Args:
            filetype: A string specifying the filetype by its extension.
                For example: "pdf" or "epub". The links are filtered by this
                extension and only links with the specified file extension are returned.

        Returns:
            A list of strings containing the download links 
        """
        # Wait for rows to load with download links
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".row")))

        # Extract download links from row elements
        download_elements = self.driver \
            .find_elements(By.CSS_SELECTOR, ".download a[href^='https://dl.humble.com']")
        download_elements = list(
            filter(lambda x: x.text.strip().lower() == filetype, download_elements)
        )
        download_links = [x.get_attribute("href") for x in download_elements]
        return download_links

    def get_download_links_by_title(self, filetype: str):
        """Retrieve links to Humble Bundle item by their titles

        Args:
            filetype: a string specifying the filetype by its extension.
                For example: "pdf" or "epub". The links are filtered by this
                extension and only links with the specified file extension are returned

        Returns:
            A dict mapping titles of items in a purchased bundle to their download links

            # TODO: add example
        """
        # Wait for rows to load with download links
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".row")))

        # Extract download titles and hrefs from row elements
        row_elements = self.driver.find_elements(By.CSS_SELECTOR, ".row")
        download_links_by_title = {}
        for row in row_elements:
            title = row.find_element(By.CSS_SELECTOR, ".title").text.strip()
            href_elements = row.find_elements(
                By.CSS_SELECTOR, ".download a[href^='https://dl.humble.com']")

            # Check each download option for matching `filetype`
            for ele in href_elements:
                if ele.text.strip().lower() == filetype:
                    download_links_by_title[title] = ele.get_attribute("href")
        return download_links_by_title

    def select_purchase(self):
        """Query user for selection of HumbleBundle purchases
        """
        purchases = self.get_purchases()
        if len(purchases) == 0:
            return

        for i, purchase in enumerate(purchases):
            print(f"{i:>3}: {purchase.text}")

        while True:
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
