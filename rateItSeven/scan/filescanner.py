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

from os import walk
from os import path
from itertools import chain

class FileScanner:
    """
    Can search files in paths
    """

    def __init__(self, dirs):
        """
        :param dirs: dirs to scan
        """
        self.scan_dirs = dirs

    def absolute_file_paths(self):
        """
        List all files recursively from the dirs to scan
        :return: list of absolute paths
        """
        for (dirpath, _, filenames) in chain.from_iterable(walk(base_dir) for base_dir in self.scan_dirs):
            for filename in filenames:
                yield path.abspath(path.join(dirpath, filename))
