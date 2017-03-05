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
from watchdog.events import FileSystemEventHandler


class EmptyEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def on_moved(self, event):
        super(EmptyEventHandler, self).on_moved(event)

    def on_created(self, event):
        super(EmptyEventHandler, self).on_created(event)

    def on_deleted(self, event):
        super(EmptyEventHandler, self).on_deleted(event)

    def on_modified(self, event):
        super(EmptyEventHandler, self).on_modified(event)


class TestWatchdogObserver(object):
    """
    Helper class to execute one run of watchdog observer and wait for the results
    """

    def __init__(self, observer):
        self._observer = observer

    def start(self):
        # Simulate thread start
        self.main_emitter().on_thread_start()

    def run_one_step(self):
        # Check directory for changes
        self.main_emitter().queue_events(timeout=0)

        # Dispatch file events and wait their resolution
        self._observer.start()
        self._observer.event_queue.join()

    def main_emitter(self):
        return next(iter(self._observer.emitters))

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, tb):
        self._observer.stop()
