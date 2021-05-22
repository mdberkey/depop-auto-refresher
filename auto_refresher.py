from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import undetected_chromedriver.v2 as uc


class auto_refresher:
    def __init__(self):
        self.driver = uc.Chrome()
        self.wait = WebDriverWait(self.driver, 20)

    def login(self, username, password):
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
        driver = self.driver
        wait = self.wait
        with driver:
            move_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#main > div.Container-sc-4caz4y-0.kgbzVC > div.styles__ProfileLinks-r941b9-8.iwqCVJ > div > button:nth-child(1)")))
            move_button.click()

    def load_all_items(self):
        driver = self.driver
        old_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(0.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == old_height:
                break
            old_height = new_height

    def get_item_links(self):
        driver = self.driver
        wait = self.wait
        item_links = []
        with driver:
            item_list = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#products-tab > div > ul > li > a")))
            sold_amt = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#main > div.Container-sc-4caz4y-0.kgbzVC > div.styles__UserInformationContainer-r941b9-0.eVIAga > div.styles__UserDetailsContainer-r941b9-2.ifmZmy > div.TrustSignalsstyles__Signals-y0jgqp-0.eEPKFu > div:nth-child(1) > span")))
            sold_amt = int(sold_amt.text.split()[0])

            for item in item_list:
                item.get_attribute("#main > div.Container-sc-4caz4y-0.kgbzVC > div.styles__UserInformationContainer-r941b9-0.eVIAga > div.styles__UserDetailsContainer-r941b9-2.ifmZmy > div.TrustSignalsstyles__Signals-y0jgqp-0.eEPKFu > div:nth-child(1) > span")
                split_link = item.get_attribute("href").split("/products/")
                edit_link = "https://www.depop.com/products/edit/" + split_link[1]
                item_links.append(edit_link)

            not_sold_amt = len(item_links) - sold_amt
            item_links = item_links[:not_sold_amt]
            item_links.reverse()
            return item_links

    def refresh_items(self, item_links):
        driver = self.driver
        wait = self.wait
        for link in item_links:
            driver.get(link)
            save_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#main > form > div.styles__Wrapper-rha4k1-0.eAgDqT > button.Button__GenericButton-sc-1js6kc1-0.styles__SaveButton-rha4k1-1.iCLdhA.Button__ButtonPrimary-sc-1js6kc1-1.bZYjzc")))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            actions = ActionChains(driver)
            actions.move_to_element(save_button).click(save_button).click(save_button).perform()

    def close_driver(self):
        sleep(10)
        self.driver.close()

#"esV3y5nvUsBm46p"

if __name__ == "__main__":
    bot = auto_refresher()
    bot.login("", "")
    bot.move_sold_items_down()
    bot.load_all_items()
    links = bot.get_item_links()
    bot.refresh_items(links)
    bot.close_driver()
