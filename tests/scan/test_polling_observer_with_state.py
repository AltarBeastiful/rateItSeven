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
from pathlib import Path, PurePath
from unittest.mock import patch

import os

from rateItSeven.scan.polling_observer_with_state import PollingObserverWithState, EmptyDirectorySnapshot
from tests.lib.test_case import RateItSevenTestCase
from tests.lib.watchdog_helper import EmptyEventHandler, TestWatchdogObserver


class TestPollingObserverWithState(RateItSevenTestCase):

    @patch.object(EmptyEventHandler, 'on_created')
    def test_should_find_all_files_if_no_previous_state(self, mock_on_created):
        # GIVEN
        observer = PollingObserverWithState(timeout=0)

        # A polling observer watching fixture directory with an empty initial state
        initial_state = EmptyDirectorySnapshot(path=self.FIXTURE_FILES_PATH)
        observer.schedule(event_handler=EmptyEventHandler(), path=self.FIXTURE_FILES_PATH, initial_state=initial_state, recursive=True)

        # Start watching directory
        with TestWatchdogObserver(observer=observer) as observer_helper:
            # Parse current directory
            observer_helper.run_one_step()

        self.assertEqual(13, mock_on_created.call_count)

    @patch.object(EmptyEventHandler, 'on_created')
    def test_should_detect_created_file(self, mock_on_created):
        new_file_path = PurePath(self.FIXTURE_FILES_PATH) / "somefile"
        try:

            # GIVEN
            # A polling observer watching fixture directory
            observer = PollingObserverWithState(timeout=0)
            observer.schedule(event_handler=EmptyEventHandler(), path=self.FIXTURE_FILES_PATH, recursive=True)

            # Start watching directory
            with TestWatchdogObserver(observer=observer) as observer_helper:

                # Create a file
                Path(new_file_path).touch(exist_ok=False)

                observer_helper.run_one_step()

            self.assertEqual(1, mock_on_created.call_count)

        finally:
            # Clean up file
            os.remove(str(new_file_path))

    @patch.object(EmptyEventHandler, 'on_created')
    def test_should_only_detect_files_not_in_inital_state(self, mock_on_created):
        new_file_path_list = [
            PurePath(self.FIXTURE_FILES_PATH) / "somefile1",
            PurePath(self.FIXTURE_FILES_PATH) / "somefile2",
        ]

        try:
            # GIVEN
            # An observer watching watching the directory
            first_observer = PollingObserverWithState(timeout=0)
            first_observer.schedule(event_handler=EmptyEventHandler(), path=self.FIXTURE_FILES_PATH, recursive=True)

            with TestWatchdogObserver(observer=first_observer) as observer_helper:
                observer_helper.run_one_step()

                # Save current directory state
                state_list = first_observer.state_list()
                self.assertEqual(1, len(state_list))

            # Create some files while no one is watching
            for new_file_path in new_file_path_list:
                Path(new_file_path).touch(exist_ok=False)

            # WHEN
            # A second observer is started with the previous state
            second_observer = PollingObserverWithState(timeout=0)
            second_observer.schedule(event_handler=EmptyEventHandler(), path=self.FIXTURE_FILES_PATH, initial_state=state_list[0].snapshot, recursive=True)

            with TestWatchdogObserver(observer=second_observer) as observer_helper:
                observer_helper.run_one_step()

            # THEN
            self.assertEqual(2, mock_on_created.call_count)

        finally:
            for new_file_path in new_file_path_list:
                os.remove(str(new_file_path))

    def test_state_list_should_be_empty_if_no_watched_directories(self):
        observer = PollingObserverWithState()

        self.assertEqual([], observer.state_list())

    def test_state_list_should_be_empty_before_start(self):
        observer = PollingObserverWithState()
        observer.schedule(event_handler=EmptyEventHandler(), path="path/1/")

        self.assertEqual([], observer.state_list())

    def test_should_list_state_of_watched_directories(self):
        observer = PollingObserverWithState()
        observer.schedule(event_handler=EmptyEventHandler(), path=self.FIXTURE_FILES_PATH)

        with TestWatchdogObserver(observer=observer) as observer_helper:
            observer_helper.run_one_step()

            state_list = observer.state_list()

        self.assertEqual(1, len(state_list))
        self.assertEqual(self.FIXTURE_FILES_PATH, state_list[0].path)
        self.assertIsNotNone(state_list[0].snapshot)
