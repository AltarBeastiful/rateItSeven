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
from unittest import skip
from unittest.mock import MagicMock, patch

import os
from watchdog.events import FileSystemEventHandler

from rateItSeven.scan.polling_observer_with_state import PollingObserverWithState
from tests.lib.test_case import RateItSevenTestCase
from tests.lib.watchdog_helper import EmptyEventHandler, TestWatchdogObserver


class TestPollingObserverWithState(RateItSevenTestCase):

    FIXTURE_PATH = os.path.abspath(__file__ + "/../../resources/files_to_scan/")

    @skip
    def test_should_find_all_files(self, mock_add):
        handler = MagicMock()

        observer = PollingObserverWithState()
        observer.schedule(event_handler=handler, path=self.FIXTURE_PATH, recursive=True)
        observer.start()

        self.assertEqual(11, mock_add.call_count)

    @patch.object(EmptyEventHandler, 'on_created')
    def test_should_detect_created_file(self, mock_on_created):
        new_file_path = PurePath(self.FIXTURE_PATH) / "somefile"
        try:

            # GIVEN
            # A polling observer watching fixture directory
            observer = PollingObserverWithState(timeout=0)
            observer.schedule(event_handler=EmptyEventHandler(), path=self.FIXTURE_PATH, recursive=True)

            # Start watching directory
            with TestWatchdogObserver(observer=observer) as observer_helper:

                # Create a file
                Path(new_file_path).touch(exist_ok=False)

                observer_helper.run_one_step()

            self.assertEqual(1, mock_on_created.call_count)

        finally:
            # Clean up file
            os.remove(str(new_file_path))
