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
import json

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
            store.persist_scanned_changes()
            os.path.isfile(self.storepath)

    def test_pullChanges_allMoviesShouldBeAdded(self):
        with MovieStore(self.storepath, [self.basedir_abspath]) as store:
            store_states = store.pull_changes()
            self.assertEqual(2, len(store_states["movies"].added))
            self.assertEqual(1, len(store_states["episodes"].added))

    def test_pullChanges_allMoviesShouldAlreadyExist(self):
        with MovieStore(self.storepath, [self.basedir_abspath]) as store:
            store.persist_scanned_changes()
            store_states = store.pull_changes()
            self.assertEqual(2, len(store_states["movies"].existing))
            self.assertEqual(1, len(store_states["episodes"].existing))

    def test_pullChanges_oneDeleted(self):
        with MovieStore(self.storepath, [self.basedir_abspath]) as store:
            #Create a video file
            movieToDeletePath = self.createFakeVideoFile()

            #Tell the store to persist changes
            store.persist_scanned_changes()

            #Remove the file and pull the changes
            os.remove(movieToDeletePath)
            store_states = store.pull_changes()

            self.assertEqual(1, len(store_states["movies"].deleted))

    def test_persist_multipleTimes_shouldRespectJsonFormat(self):
        with MovieStore(self.storepath, [self.basedir_abspath]) as store:
            store.persist_scanned_changes()
            store.persist_scanned_changes()
            try:
                json.load(open(self.storepath, "r"))
                pass
            except ValueError as e:
                self.fail("Store file badly formatted")


    def createFakeVideoFile(self):
        movieToDeletePath = self.basedir_abspath + "/movieToDelete.avi"
        movieToDelete = open(movieToDeletePath, 'w')
        movieToDelete.write("fakeContent")
        movieToDelete.close()
        return movieToDeletePath

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
