#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from functools import lru_cache

from rateItSeven.senscritique.sc_api import AuthService


class RateItSevenTestCase(unittest.TestCase):

    # Note: Must be static to avoid cache miss due to self argument
    @staticmethod
    @lru_cache()
    def authentified_user(login="legalizme@gmail.com", password="12345"):
        return AuthService().do_login(email=login, password=password)
