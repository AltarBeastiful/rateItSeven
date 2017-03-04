#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   === This file is part of RateItSeven ===
#
#   Copyright 2015, Paolo de Vathaire <paolo.devathaire@gmail.com>
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
import unittest

import os

from rateItSeven.rateitseven import RateItSeven
from rateItSeven.scan.legacy.filescanner import FileScanner


class TestRateItSeven(unittest.TestCase):
    def setUp(self):
        self.basedir_abspath = os.path.abspath(__file__ + "/../resources/files_to_scan")
        self.store_path = os.path.abspath(__file__ + "/../resources/store")
        self.login = "legalizme@gmail.com"
        self.password = "12345"
        self.scanner = FileScanner([self.basedir_abspath])
        pass

    def tearDown(self):
        if os.path.isfile(self.store_path):
            os.remove(self.store_path)

    def test_start(self):
        daemon = RateItSeven(self.login, self.password, [self.basedir_abspath], self.store_path)
        daemon.start()
        with open(self.store_path, 'r') as store:
            store_content = store.read()
        self.assertTrue("The Big Lebowski" in store_content)


if __name__ == '__main__':
    unittest.main()
