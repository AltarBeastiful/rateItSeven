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
from guessit import guessit

from rateItSeven.scan.piece import Piece


class FixtureList(object):

    piece_list = [
        Piece(path="/etc/movies/The Big Lebowski (1998).avi", guess=guessit("/etc/movies/The Big Lebowski (1998).avi")),
        Piece(path="/etc/movies/Gone.Girl.720p.mkv", guess=guessit("/etc/movies/Gone.Girl.720p.mkv")),
    ]