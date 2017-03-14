#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   === This file is part of RateItSeven ===
#
#   Copyright 2017, Rémi Benoit <r3m1.benoit@gmail.com>
#   Copyright 2017, Paolo de Vathaire <paolo.devathaire@gmail.com>
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
from unittest import skip
from unittest.mock import patch

import guessit
import os
from tinydb import JSONStorage
from tinydb import TinyDB
from watchdog.events import FileSystemEvent

from rateItSeven.scan.local_collection_store import LocalCollectionStore
from rateItSeven.scan.piece import Piece
from rateItSeven.scan.piece_crawler import PieceCrawler
from rateItSeven.scan.polling_observer_with_state import EmptyDirectorySnapshot, PollingObserverWithState
from rateItSeven.scan.remote_collection_store import RemoteCollectionStore
from rateItSeven.senscritique.domain.user import User
from rateItSeven.senscritique.sc_api import AuthService
from tests.lib.test_case import RateItSevenTestCase
from tests.lib.watchdog_helper import TestWatchdogObserver


class TestPieceCrawler(RateItSevenTestCase):
    LOCAL_COLLECTION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "my_collection.json")

    def setUp(self):
        self._clean_local_collection()

    @patch.object(AuthService, 'is_authenticated', return_value=True)
    @patch.object(PollingObserverWithState, 'schedule')
    @patch.object(PollingObserverWithState, '__init__', return_value=None)
    @patch.object(PollingObserverWithState, 'state_list', return_value=[])
    @patch.object(EmptyDirectorySnapshot, '__init__', return_value=None)
    @patch.object(RemoteCollectionStore, '__init__', return_value=None)
    @patch.object(RemoteCollectionStore, 'add')
    def test_should_add_new_piece_to_local_and_remote_collection(self, mock_add, *mocks):
        user = User(email="meme@me.com", password="1234", username="meme")
        crawler = PieceCrawler(path="some/path", user=user)

        piece_1_path = "/etc/movie/jumanji-1995.mkv"
        piece_2_path = "/etc/movie/Dikkenek (2006).avi"

        crawler.on_created(FileSystemEvent(piece_1_path))
        crawler.on_created(FileSystemEvent(piece_2_path))

        self.assertEqual([
            Piece(path=piece_1_path, guess=guessit.guessit(piece_1_path)),
            Piece(path=piece_2_path, guess=guessit.guessit(piece_2_path)),
        ], crawler.local_collection().piece_list())
        self.assertEqual(2, mock_add.call_count)

    def test_crawler_should_discover_file_in_path(self):
        crawler = PieceCrawler(path=self.FIXTURE_FILES_PATH)

        with TestWatchdogObserver(observer=crawler.file_observer()) as observer_helper:
            observer_helper.run_one_step()

        self.assertGreater(len(crawler.local_collection().piece_list()), 0)

    def test_crawler_should_only_consider_movie_files(self):
        crawler = PieceCrawler(path=self.FIXTURE_FILES_PATH)

        with TestWatchdogObserver(observer=crawler.file_observer()) as observer_helper:
            observer_helper.run_one_step()

        collection_path_list = [piece.path for piece in crawler.local_collection().piece_list()]

        normal_file_path = os.path.join(self.FIXTURE_FILES_PATH, "fake")
        self.assertNotIn(normal_file_path, collection_path_list)

        episode_1_path = os.path.join(self.FIXTURE_FILES_PATH, "Archer Season 5  (1080p H265 Joy)", "Archer S05E01 White Elephant (1080p H265 Joy).mkv")
        self.assertNotIn(episode_1_path, collection_path_list)

        movie_1_path = os.path.join(self.FIXTURE_FILES_PATH, "The Big Lebowski.mkv")
        self.assertIn(movie_1_path, collection_path_list)

    def test_crawler_should_ignore_directories(self):
        crawler = PieceCrawler(path=self.FIXTURE_FILES_PATH)
        subdir_directory_path = os.path.join(self.FIXTURE_FILES_PATH, "subdir")

        with TestWatchdogObserver(observer=crawler.file_observer()) as observer_helper:
            observer_helper.run_one_step()

        self.assertNotIn(subdir_directory_path, [piece.path for piece in crawler.local_collection().piece_list()])

    def test_should_save_local_collection_to_specified_path(self):
        # Turning on file storage as we need to persist local collection
        TinyDB.DEFAULT_STORAGE = JSONStorage

        # A crawler saving collection to a local file
        crawler = PieceCrawler(path=self.FIXTURE_FILES_PATH, local_collection_path=self.LOCAL_COLLECTION_PATH)

        self.assertEqual([], crawler.local_collection().piece_list(), "Local collection should be empty first")
        self.assertEqual([], crawler.local_collection().state_list(), "Local collection should be empty first")

        # WHEN
        with TestWatchdogObserver(observer=crawler.file_observer()) as observer_helper:
            observer_helper.run_one_step()

        # THEN
        actual_collection = LocalCollectionStore(path=self.LOCAL_COLLECTION_PATH)
        self.assertGreater(len(actual_collection.piece_list()), 0)

    def test_should_not_crawl_already_crawled_files(self):
        # Turning on file storage as we need to persist local collection
        TinyDB.DEFAULT_STORAGE = JSONStorage

        # A crawler saving collection to a local file
        crawler = PieceCrawler(path=self.FIXTURE_FILES_PATH, local_collection_path=self.LOCAL_COLLECTION_PATH)

        self.assertEqual([], crawler.local_collection().piece_list(), "Local collection should be empty first")

        # Crawl files one time, saving local collection state
        with TestWatchdogObserver(observer=crawler.file_observer()) as observer_helper:
            observer_helper.run_one_step()

        with patch.object(PieceCrawler, 'on_created') as mock_on_created:
            # Crawl again same directory
            # Using local collection previously created
            crawler = PieceCrawler(path=self.FIXTURE_FILES_PATH, local_collection_path=self.LOCAL_COLLECTION_PATH)

            # Crawl files one time, saving local collection state
            with TestWatchdogObserver(observer=crawler.file_observer()) as observer_helper:
                observer_helper.run_one_step()

            self.assertFalse(mock_on_created.called)

    def test_no_remote_collection_if_no_user_provided(self):
        crawler = PieceCrawler(self.FIXTURE_FILES_PATH)

        self.assertIsNone(crawler.remote_collection)

    @patch.object(AuthService, 'is_authenticated', return_value=False)
    def test_no_remote_collection_if_user_not_authentified(self, *mocks):
        user = User(email="meme@me.com", password="1234", username="meme")
        crawler = PieceCrawler(self.FIXTURE_FILES_PATH, user=user)

        self.assertIsNone(crawler.remote_collection)

    @patch.object(AuthService, 'is_authenticated', return_value=False)
    @patch.object(RemoteCollectionStore, '__init__', return_value=None)
    def test_should_open_remote_collection_with_specified_title(self, mock_remote_collection, *mocks):
        user = User(email="meme@me.com", password="1234", username="meme")

        # WHEN
        PieceCrawler(self.FIXTURE_FILES_PATH, user=user, remote_collection_title="some list")

        # THEN
        mock_remote_collection.assert_called_once_with(user=user, movie_collection_title="some list")

    def _is_local_collection_empty(self):
        local_collection = LocalCollectionStore(self.LOCAL_COLLECTION_PATH)

        return local_collection.piece_list() == [] and local_collection.state_list == []

    def _clean_local_collection(self):
        try:
            if not self._is_local_collection_empty():
                os.remove(self.LOCAL_COLLECTION_PATH)
        except:
            pass
