'''
Created on Apr 20, 2015

@author: remi
'''
from selenium.webdriver.remote.webdriver import WebDriver

class Page(object):

    def to(self, driver : WebDriver):
        self._driver = driver

        driver.get(self.url())

    def url(self):
        return self._url

class TopBanner(Page):

    def alreadySuscribed(self):
        return '//*[@id="wrap"]/header/div[1]/div/div/div/div'

    def loginField(self):
        return '//*[@id="wrap"]/header/div[1]/div/div/div/div/form/input[1]'

    def passwordField(self):
        return '//*[@id="wrap"]/header/div[1]/div/div/div/div/form/input[2]'

    def submitLoginButton(self):
        return '//*[@id="wrap"]/header/div[1]/div/div/div/div/form/fieldset/input'

class HomePage(TopBanner):

    def __init__(self):
        self._url = 'http://www.senscritique.com/'

class UserPage(TopBanner):
    BASE_URL = 'http://www.senscritique.com/'

    def __init__(self, username):

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

