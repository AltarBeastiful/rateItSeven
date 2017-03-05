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
import os

from watchdog.utils import stat as default_stat
from watchdog.observers.api import BaseObserver, DEFAULT_OBSERVER_TIMEOUT, DEFAULT_EMITTER_TIMEOUT, ObservedWatch
from watchdog.observers.polling import PollingEmitter
from watchdog.utils.dirsnapshot import DirectorySnapshot


class EmptyDirectorySnapshot(DirectorySnapshot):

    def __init__(self, path, recursive=True, walker_callback=None, stat=default_stat, listdir=None):
        self._stat_info = {}
        self._inode_to_path = {}

        st = stat(path)
        self._stat_info[path] = st
        self._inode_to_path[(st.st_ino, st.st_dev)] = path


class PollingEmitterWithState(PollingEmitter):

    def __init__(self, event_queue, watch, timeout=DEFAULT_EMITTER_TIMEOUT, initial_state=None):
        super(PollingEmitterWithState, self).__init__(event_queue, watch, timeout)

        if initial_state is not None:
            self._snapshot = initial_state

    # Disable initial directory snapshot
    def on_thread_start(self):
        if self._snapshot is None:
            super(PollingEmitterWithState, self).on_thread_start()

    def current_snapshot(self):
        return self._snapshot


class PollingObserverWithState(BaseObserver):
    """
    Platform-independent observer that polls a directory to detect file
    system changes.
    """

    def __init__(self, timeout=DEFAULT_OBSERVER_TIMEOUT):
        BaseObserver.__init__(self, emitter_class=PollingEmitterWithState, timeout=timeout)

    def schedule(self, event_handler, path, recursive=False, initial_state=None):
        """
        Schedules watching a path and calls appropriate methods specified
        in the given event handler in response to file system events.

        :param initial_state:
            The previous state of the directory. Files changes happened after the initial_state will be considered,
            previous events will be ignored.
        :type initial_state:
            :class:`DirectorySnapshot`
        :param from_scratch:
            If True will consider all files in path as new
        :type from_scratch:
            ``bool``
        :param event_handler:
            An event handler instance that has appropriate event handling
            methods which will be called by the observer in response to
            file system events.
        :type event_handler:
            :class:`watchdog.events.FileSystemEventHandler` or a subclass
        :param path:
            Directory path that will be monitored.
        :type path:
            ``str``
        :param recursive:
            ``True`` if events will be emitted for sub-directories
            traversed recursively; ``False`` otherwise.
        :type recursive:
            ``bool``
        :return:
            An :class:`ObservedWatch` object instance representing
            a watch.
        """
        with self._lock:
            watch = ObservedWatch(path, recursive)
            self._add_handler_for_watch(event_handler, watch)

            # If we don't have an emitter for this watch already, create it.
            if self._emitter_for_watch.get(watch) is None:
                emitter = self._emitter_class(event_queue=self.event_queue,
                                              watch=watch,
                                              timeout=self.timeout,
                                              initial_state=initial_state)
                self._add_emitter(emitter)
                if self.is_alive():
                    emitter.start()
            self._watches.add(watch)
        return watch

    def state_list(self):
        """
        Saves the states of all watches
        :return: list(DirectorySnapshot)
        """
        state_list = []
        for emitter in self.emitters:
            state_list.append(emitter.current_snapshot())

        return state_list
