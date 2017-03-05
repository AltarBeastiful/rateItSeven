#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from itertools import islice

from functools import lru_cache
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from rateItSeven.senscritique.sc_api import AuthService


class RateItSevenTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        TinyDB.DEFAULT_STORAGE = MemoryStorage

    # Note: Must be static to avoid cache miss due to self argument
    @staticmethod
    @lru_cache()
    def authentified_user(login="legalizme@gmail.com", password="12345"):
        return AuthService().do_login(email=login, password=password)

    def assertCountGreater(self, iterable, minimum, msg=None):
        """
        Assert iterable has at least 'minimum' elements
        """
        first_n_element = list(islice(iterable, 0, minimum + 1))
        self.assertGreater(len(first_n_element), minimum, msg)
