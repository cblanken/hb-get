"""Selenium driver and utility functions for interfacing with the HumbleBundle website.

Typical usage example:

    hb = HumbleDriver("https://www.humblebundle.com")
    if hb.login():
        purchases = hb.get_purchases()
        hb.select_purchase()
        download_links_by_title = hb.get_download_links_by_title(args.filetype)
        for title,link in download_links_by_title.items():
            print(title, link)
"""
from getpass import getpass
import os
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class HumblePageExpectedConditions(Enum):
    """Enum for indicating current page of HumbleDriver"""
    MAIN = EC.title_contains("Humble Bundle | game bundles, book bundles") # Main page
    HOME = EC.url_matches("https://www.humblebundle.com/home/")
    LOGIN_USER_PASS = EC.text_to_be_present_in_element((By.CSS_SELECTOR, "h1.header"), "Log In") # user/pass login page
    LOGIN_MFA = EC.text_to_be_present_in_element((By.CSS_SELECTOR, "h1.header"), "Verify Account") # MFA page

class HumbleDriver:
    """Selenium driver class"""
    def __init__(self, url: str, max_auth_time: float = 1.0):
        self.base_url = url
        self.max_auth_time = max_auth_time

        # Initialize Selenium browser driver
        opts = ChromeOptions()
        opts.add_argument("--window-size=1600,900")
        # opts.add_argument("--headless=new")

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

    def _login_mfa_verify(self):
        """Initiate MFA response

        Note: It is assumed the driver is on the correct MFA response
            page, incorrect state of the the driver will cause a failed
            login attempt

        Returns:
            True: if user/password were correct and login was successful
            False: if the login failed in any way
        """
        mfa_code = input("Please enter your MFA code: ")
        mfa_form = self.driver.find_element(By.NAME, "code")
        mfa_form.clear()
        mfa_form.send_keys(mfa_code)

        mfa_form_submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type=submit]")
        mfa_form_submit_btn.click()

        # An invalid MFA code was provided
        try:
            input_status = WebDriverWait(self.driver, self.max_auth_time).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".input-status"))).text
        except TimeoutException:
            # The provided MFA code was correct
            return True

        if "invalid token" in input_status.lower():
            print(f"Login failed with \"{input_status.strip()}\"")
            again = input("Try re-entering MFA? (y/n): ")
            if again.lower() == 'y':
                return self._login_mfa_verify()
            else:
                return False

    def _login_user_pass(self, user: str = None, password: str = None):
        """Initiate login with username and password

        Note: It is assumed the driver is on the correct login page
            at www.humblebundle.com/login, incorrect state of the the
            driver will cause a failed login attempt

        Returns:
            True: if user/password were correct and login was successful
            False: if the login failed in any way
        """
        try:
            # Submit login for
            form_user = self.driver.find_element(By.NAME, "username")
            if user is None:
                user = input("Please provide your HumbleBundle username: ")
            form_user.clear()
            form_user.send_keys(user)

            form_pass = self.driver.find_element(By.NAME, "password")
            if password is None:
                password = getpass("Please provide your HumbleBundle password: ")
            form_pass.clear()
            form_pass.send_keys(password)

            form_submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type=submit]")
            form_submit_btn.click()

        except NoSuchElementException as exc:
            print(f"A page element required for login could not be found. {exc.msg}")
            return False

        # Wait for one of the following possible pages
        try:
            WebDriverWait(self.driver, 1).until(EC.any_of(
                HumblePageExpectedConditions.LOGIN_MFA,
                HumblePageExpectedConditions.MAIN,
                HumblePageExpectedConditions.HOME,
            ))
            return True
        except TimeoutException:
            # An invalid user/password combination was used
            try:
                input_status = WebDriverWait(self.driver, self.max_auth_time).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".input-status"))).text
                if "don't match" in input_status.lower():
                    print(f"Login failed with: \"{input_status.strip()}\"")
                    again = input("Try again? (y/n): ")
                    if again.lower() == 'y':
                        return self._login_user_pass()
                    else:
                        return False
                else:
                    print("The provided user/password were incorrect, but no error message was provided.")
                    return False
            except TimeoutException:
                # The provided user/password were correct
                return True


    def login(self,
              user: str = os.environ.get("HBGET_USER"),
              password: str = os.environ.get("HBGET_PASS")):
        """Authenticate user on the HumbleBundle login page.

        Note: It is recommended to provide these values via the default
            environment variables HBGET_USER and HBGET_PASS.

        Args:
            user: A string of the user's HumbleBundle username.
            password: A string of the user's HumbleBundle password.

        Returns:
            True: if login was successful
            False: if login failed
        """
        # Navigate to login page
        print("Logging in...")
        self.driver.get(self.base_url + "/login")

        if self._login_user_pass(user, password):
            # Username and password were correct
            print("The provided username and password were correct.")

            # Checking for MFA
            try:
                self.auth_wait.until(EC.any_of(
                    HumblePageExpectedConditions.MAIN,
                    HumblePageExpectedConditions.HOME
                ))
                print("Successfully logged in.")
                return True
            except TimeoutException:
                self.auth_wait.until(HumblePageExpectedConditions.LOGIN_MFA)
                print("MFA (multi-factor authentication) is enabled")
                if self._login_mfa_verify():
                    print("The provided MFA code was correct.")
                    print("Successfully logged in.")
                    return True


    def get_purchases(self) -> list:
        """Retrieves a list of elements corresponding to the purchases of user.

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

    def get_download_links_by_filename(self, filetype: str):
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
                    download_links_by_title[title + "." + filetype] = ele.get_attribute("href")
        return download_links_by_title

    def select_purchase(self, includes_str: str):
        """Query user for selection of HumbleBundle purchases
        """
        purchases_titles = [" ".join(x.text.split()[:-4])
                            for x in self.get_purchases() if includes_str in x.text]
        if len(purchases_titles) == 0:
            return

        for i, purchase in enumerate(purchases_titles):
            print(f"{i:>3}: {purchase}")

        while True:
            sel = input(f"Select one above purchases (0-{len(purchases_titles)}): ")
            try:
                sel = int(sel)
                if sel < 0 or sel > len(purchases_titles):
                    continue
                key = self.get_purchases()[sel].get_attribute("data-hb-gamekey")
                self.driver.get(f"{self.base_url}/downloads?key={key}")
                return purchases_titles[sel]
            except ValueError:
                continue
