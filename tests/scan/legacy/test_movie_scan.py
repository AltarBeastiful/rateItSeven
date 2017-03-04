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

from rateItSeven.scan.legacy.moviescanner import MovieScanner


class TestMovieScan(unittest.TestCase):

    def setUp(self):
        self.basedir_abspath = os.path.abspath(__file__ + "/../../../resources/files_to_scan")
        pass

    def test_listallMovies(self):
        movies_count = 0
        moviescan = MovieScanner([self.basedir_abspath])
        for _ in moviescan.list_movies():
            movies_count += 1
        self.assertEqual(2, movies_count)

    def test_list_episodes(self):
        episode_count = 0
        moviescan = MovieScanner([self.basedir_abspath])
        for _ in moviescan.list_episodes():
            episode_count += 1
        self.assertEqual(1, episode_count)

if __name__ == "__main__":
    unittest.main()
