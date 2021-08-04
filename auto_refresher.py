""" This module allows Depop store owners to automatically refresh their listings 24/7."""
from time import sleep
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver.v2 as uc


class AutoRefresher:
    """ This class can login, move sold items to bottom, and refresh listings for a depop profile"""

    def __init__(self, indefinite=False, frequency=3600):
        self.driver = uc.Chrome()
        self.wait = WebDriverWait(self.driver, 20)
        self.indefinite = indefinite
        self.frequency = frequency

    def login(self, username, password):
        """
        Logins to user's profile
        :param username: username of store owner
        :param password: password of store owner
        :return: True if successful
        """
        driver = self.driver
        wait = self.wait
        with driver:
            driver.get("https://www.depop.com/login/")
            username_input = driver.find_element_by_id("username")
            password_input = driver.find_element_by_id("password")
            username_input.send_keys(username)
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            wait.until(EC.title_is("Depop - buy, sell, discover unique fashion"))
            driver.get("https://www.depop.com/" + username.lower())
        return True

    def move_sold_items_down(self):
        """
        Moves the sold items down on the user's depop profile (Must be logged in first)
        :return: True if successful
        """
        driver = self.driver
        wait = self.wait
        with driver:
            move_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#main > div.Container-sc-1t5af73-0.hFJMpP"
            " > div.styles__ProfileLinks-r941b9-8.iwqCVJ > div > button:nth-child(1)")))
            move_button.click()
        return True

    def load_all_items(self):
        """
        Scrolls to bottom of store page to load all items
        :return: True if successful
        """
        driver = self.driver
        old_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(0.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == old_height:
                break
            old_height = new_height
        return True

    def get_item_links(self):
        """
        Retrieves reversed list of all non-sold items in store
        :return: reversed href links to each non-sold item
        """
        driver = self.driver
        wait = self.wait
        item_links = []
        with driver:
            item_list = wait.until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#products-tab > div > ul > li > a")))
            sold_amt = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#main > div.Container-sc-1t5af73-0.hFJMpP"
            " > div.styles__UserInformationContainer-r941b9-0.eVIAga > div.styles__UserDetailsContainer-r941b9-2.ifmZmy"
            " > div.TrustSignalsstyles__Signals-y0jgqp-0.eEPKFu > div:nth-child(1) > p")))
            sold_amt = int(sold_amt.text.split()[0])

            for item in item_list:
                item.get_attribute("#products-tab > div > ul > li:nth-child(3) > a")
                split_link = item.get_attribute("href").split("/products/")
                edit_link = "https://www.depop.com/products/edit/" + split_link[1]
                item_links.append(edit_link)

            not_sold_amt = len(item_links) - sold_amt
            item_links = item_links[:not_sold_amt]
            item_links.reverse()
            return item_links

    def refresh_items(self, item_links):
        """
        Refreshes all non-sold items
        :param item_links: Reversed list of non-sold items
        :return: True if successful
        """
        driver = self.driver
        wait = self.wait
        for link in item_links:
            driver.get(link)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#main > form > div.styles__Wrapper-rha4k1-0."
            "eAgDqT > button.Button__GenericButton-sc-1js6kc1-0.styles__SaveButton-rha4k1-1.iCLdhA.Button__ButtonPrimar"
            "y-sc-1js6kc1-1.bZYjzc")))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            save_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#main > form > div.styles__Wra"
            "pper-rha4k1-0.eAgDqT > button.Button__GenericButton-sc-1js6kc1-0.styles__SaveButton-rha4k1-1.iCLdhA.Button"
            "__ButtonPrimary-sc-1js6kc1-1.bZYjzc")))

            while True:
                ActionChains(driver).move_to_element(save_button).click(save_button).perform()
                try:
                    WebDriverWait(self.driver, 3).until(EC.staleness_of(save_button))
                    break
                except TimeoutException:
                    continue
        if self.indefinite:
            print("Successfully refreshed listings.")
            for i in range(int(self.frequency / 10)):
                sleep(10)
                try:
                    driver.find_element_by_id("__next")
                except NoSuchWindowException:
                    break
            self.refresh_items(item_links)
        return True

    def close_driver(self):
        """
        Closes chrome driver
        :return: True if successful
        """
        sleep(5)
        self.driver.close()
        return True

    def accept_cookies(self):
        driver = self.driver
        wait = self.wait
        button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#__next > div.sc-kEYyzF.kzcxAl > div.sc-iAyFgw.JSbHK > button.sc-gZMcBi.sc-gqjmRU.sc-eHgmQL.jDewdN"))) 
        ActionChains(driver).move_to_element(button).click(button).perform()


if __name__ == "__main__":
    bot = AutoRefresher(indefinite=True, frequency=10)
    bot.login("username", "password")
    bot.move_sold_items_down()
    #bot.accept_cookies()
    bot.load_all_items()
    links = bot.get_item_links()
    bot.refresh_items(links)
    bot.close_driver()
