#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   === This file is part of RateItSeven ===
#
#   Copyright 2015, Rémi Benoit <r3m1.benoit@gmail.com>
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
from setuptools import setup, find_packages
from rateItSeven import __version__
from rateItSeven.conf.global_settings import APP_NAME

setup(name=APP_NAME,
      version=__version__.__version__,
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'rateItSeven = rateItSeven.__main__:main'
          ]
      },
      license='GPL version 3',
      author='Rémi Benoit, Paolo de Vathaire',
      url='https://github.com/AltarBeastiful/rateItSeven',
      keywords=['SensCritique', 'Sens Critique', 'library', 'media' , 'movie', 'serie', 'film'],
      test_suite='tests'
      )
