#   === This file is part of RateItSeven ===
#
#   Copyright 2015, Rémi Benoit <r3m1.benoit@gmail.com>
#
#   RateItSeven is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   RateItSeven is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with RateItSeven. If not, see <http://www.gnu.org/licenses/>.
#

from types import MethodType

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from rateItSeven.sclist import SCList
from time import sleep

DEFAULT_TIMEOUT = 5
NEXTPAGE_TIMEOUT = 20

class Page(object):

    def __init__(self):
        self._driver = None


    # TODO: should check if you're already 'at' the page. Don't get the page if it's the case
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

    def q(self, xpath, timeout = DEFAULT_TIMEOUT, condition=EC.visibility_of_element_located, driver = None):
        # Default node is the root node
        if driver is None:
            driver = self._driver

        # We should have a valid node at this point
        if driver is None:
            return None

        try:
            node = self.waitForNode(xpath, condition, timeout, driver)
            self.decorateNode(node)
        except (NoSuchElementException, TimeoutException):
            node = None

        return node

    def qs(self, xpath):
        return [self.decorateNode(n) for n in self._driver.find_elements_by_xpath(xpath)]

    def waitForNode(self, xpath, condition, timeout=10, driver = None):
        if driver is None:
            driver = self._driver

        return WebDriverWait(driver, timeout).until(condition((By.XPATH, xpath)))

class Module(Page):

    def __init__(self, root_node):
        self._root = root_node
        self._driver = root_node._driver

    def qs(self, xpath):
        return [self.decorateNode(n) for n in self._root.find_elements_by_xpath(xpath)]

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

    def currentUser(self, timeout = DEFAULT_TIMEOUT):
        return self.q('//*[@id="wrap"]/header/div[1]/div/div/div/a[3]', timeout)

    def username(self, timeout = DEFAULT_TIMEOUT):
        currentUserNode = self.currentUser(timeout)
        if currentUserNode is None:
            return None
        else:
            children = currentUserNode.children()
            return children[1]

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
        self._current_page = 1

    def at(self):
        self.waitForNode('//*[@id="wrap"]/div[4]/div[2]/div/button', EC.element_to_be_clickable)

    def lists(self):
        next_page = True

        while next_page:
            for node in self.list_nodes():
                yield ListModule(node)

            self._current_page += 1
            next_button = self.page_button(self._current_page)

            next_page = next_button is not None
            if next_page:
                next_button.click()
                # Wait till the next page is loaded
                self.current_page_is(self._current_page)

    def list_nodes(self):
        return self.qs('//*[@id="wrap"]/div[4]/div[3]/ul/li')

    def page_button(self, i):
        return self.q('//*[@data-sc-pager-page="' + str(i) + '"]', 0)

    def current_page_is(self, i):
        return self.q('//span[@data-sc-pager-page="' + str(i) + '"]', NEXTPAGE_TIMEOUT)

    def create_list_button(self):
        return self.q('//*[@data-rel="sc-list-new"]')

    def new_list_title(self):
        return self.q('//*[@data-rel="new-list-label"]')

    def film_type_radio(self):
        return self.q('//*[@id="list-type1"]')

    def classic_list_radio(self):
        return self.q('//*[@id="list-isUnordered"]')

    def confirm_create_list_button(self):
        return self.q('//*[@data-rel="submit-new-list"]')

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
        self._list = l
        self._current_page = 1

    def url(self):
        return "http://www.senscritique.com/liste/" + self._list.title().replace(' ', '_') + "/" + self._list.id()

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
                # Wait till the next page is loaded
                self.current_page_is(self._current_page)

    def page_button(self, folio):
        return self.q('//*[@data-sc-pager-page="' + str(folio) + '"]', 0)

    def current_page_is(self, i):
        return self.q('//span[@data-sc-pager-page="' + str(i) + '"]', NEXTPAGE_TIMEOUT)

    def query_input(self):
        return self.q('//*[@id="new-list-item"]')

    def add_movie_button(self, index):
        return self.q('//*[@id="new-item-results"]/li[' + str(index + 1) + ']/div[2]/form/fieldset/button', 8)

    def movie_description_field(self, index):
        return self.q('//*[@id="new-item-results"]/li[' + str(index + 1) + ']/div[2]/form/fieldset/textarea', 8)

    def description_node(self):
        return self.q('//*[@id="description-update"]')

    def description(self):
        if "elme-description-update" in self.description_node().get_attribute("class"):
            return self.description_node().value()
        else:
            return ""

    def description_field(self):
        return self.q('//textarea[@name="description"]')

    def save_description_button(self):
        return self.q('//input[contains(concat(" ", normalize-space(@class), " "), " d-button-success ")]')

    def set_description(self, description):
        self.description_node().click()

        field = self.description_field()
        field.clear()
        field.send_keys(description)

        self.save_description_button().click()

    def wait_loading_finished(self):
        WebDriverWait(self._driver, NEXTPAGE_TIMEOUT).until(
            EC.invisibility_of_element_located((By.XPATH, '//div[@data-rel="list-content" and contains(concat(" ", normalize-space(@class), " "), " d-loader-container ")]'))
        )

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
        return "" if len(descriptionNode) == 0 else descriptionNode[0].value()

    def delete_button(self):
        return self.q('//*[@data-rel="sc-item-delete"]', NEXTPAGE_TIMEOUT, EC.visibility_of_element_located, self._root)

    def confirm_delete_button(self):
        return self.q('//button[@data-rel="sc-message-button-ok"]')

