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
from rateItSeven.sclist import SCList


class Page(object):

    def __init__(self):
        self._driver = None


    def to(self, driver : WebDriver):
        self._driver = driver

        driver.get(self.url())

        try:
            self.at()
        except AttributeError:
            pass

    def url(self):
        return self._url


    def decorateNode(self, node):
        node._driver = self._driver

        hover = lambda self: ActionChains(self._driver).move_to_element(self).perform()
        node.hover = MethodType(hover, node)

        node.decorateNode = MethodType(self.decorateNode.__func__, node)

        children = lambda self: [self.decorateNode(e) for e in self.find_elements_by_xpath("*")]
        node.children = MethodType(children, node)

        value = lambda self: self.get_attribute('innerHTML')
        node.value = MethodType(value, node)

        return node

    def q(self, xpath, timeout = 5, condition = EC.presence_of_element_located):
        if self._driver is None:
            return None

        try:
            node = self.waitForNode(xpath, condition, timeout)
            self.decorateNode(node)
        except (NoSuchElementException, TimeoutException):
            node = None

        return node

    def qs(self, xpath):
        return [self.decorateNode(n) for n in self._driver.find_elements_by_xpath(xpath)]

    def waitForNode(self, xpath, condition, timeout = 10):
        return WebDriverWait(self._driver, timeout).until(condition((By.XPATH, xpath)))

class Module(object):

    def __init__(self, root_node):
        self._root = root_node

    def qs(self, xpath):
        return [self.decorateNode(n) for n in self._root.find_elements_by_xpath(xpath)]

    def decorateNode(self, node):
        node.decorateNode = MethodType(self.decorateNode.__func__, node)

        children = lambda self: [self.decorateNode(e) for e in self.find_elements_by_xpath("*")]
        node.children = MethodType(children, node)

        value = lambda self: self.get_attribute('innerHTML')
        node.value = MethodType(value, node)

        return node

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

    def currentUser(self):
        return self.q('//*[@id="wrap"]/header/div[1]/div/div/div/a[3]');

    def username(self):
        if self.currentUser() is None:
            return None
        else:
            childs = self.currentUser().children()
            return childs[1]

    def loginError(self):
        return self.q('//*[@id="wrap"]/header/div[1]/div/div/div/div/form/fieldset/p')

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

    def at(self):
        self.waitForNode('//*[@id="wrap"]/div[4]/div[2]/div/button', EC.element_to_be_clickable)

    def lists(self):
        return [ListModule(n) for n in self.qs('//*[@id="wrap"]/div[4]/div[3]/ul/li')]

class ListModule(Module):
    def __init__(self, root):
        super().__init__(root)
        self._children = self._root.children()

    def id(self):
        return self.url().split('/')[-1]

    def url(self):
        return self._children[1].get_attribute('href')

    def title(self):
        return self._children[1].get_attribute('title')

    def description(self):
        if len(self._children) < 3:
            return None
        else:
            return self._children[2].value()

class ListPage(TopBanner):

    def __init__(self, l : SCList):
        super().__init__()
        self._url = "http://www.senscritique.com/liste/" + l.title().replace(' ', '_') + "/" + l.id()
        self._current_page = 1

    def movie_nodes(self):
        return self.qs('//*[@data-rel="list-item"]')

    def movies(self):
        next_page = True

        while next_page:
            for node in self.movie_nodes():
                yield MovieModule(node)

            self._current_page += 1
            next_button = self.page_button(self._current_page)

            next_page = next_button is not None
            if next_page:
                next_button.click()

    def page_button(self, folio):
        return self.q('//*[@data-sc-pager-page="' + str(folio) + '"]', 0)

    def query_input(self):
        return self.q('//*[@id="new-list-item"]')

    def add_movie_button(self, index):
        return self.q('//*[@id="new-item-results"]/li[' + str(index + 1) + ']/div[2]/form/fieldset/button', 8)

class MovieModule(Module):

    def __init__(self, node):
        super().__init__(node)
        self._title_node = self.qs('div[2]/h3/a')[0]

    def url(self):
        return self._title_node.get_attribute('href')

    def title(self):
        return self._title_node.value()

    def description(self):
        descriptionNode = self.qs('div[2]/div[2]/div')
        return None if len(descriptionNode) == 0 else descriptionNode[0].value()
