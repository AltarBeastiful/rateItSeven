#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pip install pysynthetic requests lxml
"""

import unittest

from contracts import new_contract

import requests
from lxml import html
from lxml.html import HtmlElement
from synthetic import synthesize_constructor
from synthetic import synthesize_property

@synthesize_constructor()
@synthesize_property('cookies')
@synthesize_property('login')
@synthesize_property('password')
class User(object):

    def __init__(self):
        pass

class SensCritique(object):

    def do_login(self, user: User):
        url = "https://www.senscritique.com/sc2/auth/login.json"
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'dnt': '1', 'referer': 'https://www.senscritique.com/',
            'cookie': 'SC_SESSIONS_ID=hc7gm9tn2ih961oo437g1ipch2; SC_DYNAMIC_ELEMENT941=1487891615; SC_DEVICE_CATEGORY=desktop; __cfduid=dde63f616ee8fb70abe4e5785732f83791487891615',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'accept-encoding': 'gzip, deflate, br',
            'origin': 'https://www.senscritique.com', 'x-requested-with': 'XMLHttpRequest',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-newrelic-id': 'VQUCU1NUABABXVJQBwIOVg==',
            'accept-language': 'en,en-US;q=0.8,ja;q=0.6,fr;q=0.4,de;q=0.2,en-ZA;q=0.2'
        }

        data = {
            'email': user.login,
            'pass': user.password,
        }

        response = requests.post(url, headers=headers, data=data)

        user.cookies = response.cookies

        return response


new_contract('HtmlElement', HtmlElement)


@synthesize_constructor()
@synthesize_property('node', contract='HtmlElement')
class ListModule(object):
    def __init__(self):
        self._children = self.node.getchildren()

    def url(self):
        return self.title_node().get('href')

    def title(self):
        return self.title_node().get('title')

    def description(self):
        if len(self._children) < 3:
            return None
        else:
            return self._children[2].text

    def title_node(self):
        for child in self._children:
            if child.tag == "a":
                return child


class TestLoginRequest(unittest.TestCase):

    LIST_NODES_XPATH = '//div[@data-rel="lists-content"]/ul/li'

    def test_login_success(self):
        user = User(login="legalizme@gmail.com", password="12345")

        response = SensCritique().do_login(user=user)

        self.assertEqual(200, response.status_code)
        self.assertNotEqual(0, len(user.cookies))

        # Authentified requests

        # Main page
        response = requests.get("https://www.senscritique.com/?logged=true?logged=1", cookies=user.cookies)
        self.assertIn(u"invite-san", response.text)

        # Get lists
        response = requests.get("https://www.senscritique.com/invite-san/listes/likes", cookies=user.cookies)
        tree = html.fromstring(response.content)
        lists = [ListModule(node=node) for node in tree.xpath(self.LIST_NODES_XPATH)]

        self.assertEqual("Une liste", lists[0].title())
        self.assertEqual("une descri", lists[0].description())
        self.assertEqual("/liste/Une_liste/1622651", lists[0].url())





