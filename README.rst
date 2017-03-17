RateItSeven
===========

.. image:: https://travis-ci.org/AltarBeastiful/rateItSeven.svg
    :target: https://travis-ci.org/AltarBeastiful/rateItSeven
    :alt: Build Status

.. image:: https://coveralls.io/repos/github/AltarBeastiful/rateItSeven/badge.svg?branch=master
    :target: https://coveralls.io/github/AltarBeastiful/rateItSeven?branch=master
    :alt: Build tests coverage

RateItseven est un programme python permettant de vous aider à établir une bibliothèque de vos fichiers
multimedia sur `SensCritique <https://www.senscritique.com>`_.
Pour ce faire, RateItSeven va créer une liste de film sur votre compte `SensCritique <https://www.senscritique.com>`_
et y insérer chaque film trouvé dans les dossiers spécifiés.

Installation
============
RateItSeven n'a pas été encore officiellement publié.

Vous pouvez cependant l'installer très simplement à partir des sources avec `pip <http://www.pip-installer.org/>`_::

    $ python3 -m pip install https://github.com/AltarBeastiful/rateItSeven/archive/statelessAPI.zip

Utilisation
===========
Une fois installé, RateItSeven peut-être utilisé via la ligne de commande : ::

    $ rateItSeven

    usage: rateItSeven [-h] [-u USERNAME] [-p PASSWORD] [-f STORE_FILE]
                       [-m MOVIE_LIST] [-s SERIE_LIST] [-v] [--version]
                       [paths [paths ...]]

    positional arguments:
      paths                 The path to your movie library folder (you can specify
                            more than one)

    optional arguments:
      -h, --help            show this help message and exit
      -u USERNAME, --username USERNAME
                            Your SensCritique user name
      -p PASSWORD, --password PASSWORD
                            Your SensCritique password
      -f STORE_FILE, --storefile STORE_FILE
                            Specify a specific store file previously created by
                            another run of RateItSeven or a path to a nonexistant
                            file that will be created by RateItSeven
      -m MOVIE_LIST, --movielist MOVIE_LIST
                            The name of the SensCritique list where to store your
                            movie library
      -s SERIE_LIST, --serielist SERIE_LIST
                            The name of the SensCritique list where to store your
                            serie library
      -v, --verbose         Display debug output
      --version             Display the rateItSeven version.


