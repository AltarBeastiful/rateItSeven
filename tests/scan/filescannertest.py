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

import os
import unittest
import pathlib

from rateItSeven.scan.filescanner import FileScanner

class TestFileScanner(unittest.TestCase):

    def setUp(self):
        self.basedir_abspath = os.path.abspath(__file__ + "/../../resources/files_to_scan")
        self.scanner = FileScanner([self.basedir_abspath])

        pass

    def test_findFirstLevelFile(self):
        path_to_find = self.basedir_abspath + "/fake"
        self.assertIn(pathlib.Path(path_to_find).as_uri(),
                      list(pathlib.Path(pathFound).as_uri() for pathFound in self.scanner.absolute_file_paths()),
                      "first level file not found")

    def test_findSubLevelFile(self):
        path_to_find = self.basedir_abspath + "/subdir/fake"
        self.assertIn(pathlib.Path(path_to_find).as_uri(),
                      list(pathlib.Path(pathFound).as_uri() for pathFound in self.scanner.absolute_file_paths()),
                      "sub level file not found")

    def test_findallFiles(self):
        files_to_find_count = 10
        self.assertEqual(files_to_find_count, len(list(self.scanner.absolute_file_paths())))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()