'''
Created on Apr 20, 2015

@author: remi
'''
from types import MethodType

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Page(object):

    def __init__(self):
        self._driver = None


    def to(self, driver : WebDriver):
        self._driver = driver

        driver.get(self.url())

    def url(self):
        return self._url


    def decorateNode(self, node):
        node._driver = self._driver

        hover = lambda self: ActionChains(self._driver).move_to_element(self).perform()
        node.hover = MethodType(hover, node)

        return node

    def q(self, xpath, timeout = 2, condition = EC.presence_of_element_located):
        if self._driver is None:
            return None

        try:
            node = self.waitForNode(xpath, condition, timeout)
            self.decorateNode(node)
        except (NoSuchElementException, TimeoutException):
            node = None

        return node

    def waitForNode(self, xpath, condition, timeout = 10):
        return WebDriverWait(self._driver, timeout).until(condition((By.XPATH, xpath)))

class TopBanner(Page):

    def __init__(self):
        super().__init__()

    def alreadySuscribed(self):
        return self.q('//*[@id="wrap"]/header/div[1]/div/div/div/div')

    def loginField(self):
        return self.q('//*[@id="wrap"]/header/div[1]/div/div/div/div/form/input[1]')

    def passwordField(self):
        return self.q('//*[@id="wrap"]/header/div[1]/div/div/div/div/form/input[2]')

    def submitLoginButton(self):
        return self.q('//*[@id="wrap"]/header/div[1]/div/div/div/div/form/fieldset/input')

class HomePage(TopBanner):

    def __init__(self):
        super().__init__()
        self._url = 'http://www.senscritique.com/'

class UserPage(TopBanner):
    BASE_URL = 'http://www.senscritique.com/'

    def __init__(self, username):
        super().__init__()
        self._username = username
        self._url = self.BASE_URL + username

class ListCollectionPage(UserPage):
    '''
    classdocs
    '''


    def __init__(self, username):
        '''
        Constructor
        '''
        super().__init__(username)
        self._url += "/listes/likes"
