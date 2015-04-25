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

import os
import unittest

from rateItSeven.scan.moviestore import MovieStore


class TestMovieStore(unittest.TestCase):

    def setUp(self):
        self.basedir_abspath = os.path.abspath(__file__ + "/../../resources/files_to_scan")
        self.storepath = os.path.abspath(__file__ + "/../../resources/store")

    def tearDown(self):
        if os.path.isfile(self.storepath):
            os.remove(self.storepath)

    def test_persist_shouldCreateFile(self):
        with MovieStore(self.storepath, [self.basedir_abspath]) as store:
            store.persist()
            os.path.isfile(self.storepath)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()