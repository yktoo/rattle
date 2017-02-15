# Rattle
[![Build Status](https://travis-ci.org/yktoo/rattle.svg?branch=master)](https://travis-ci.org/yktoo/rattle)

This is **Rattle**, a modular and lightweight ETL (**E**xtract, **T**ransform, **L**oad) application.


## Requirements

1. Python v3.4.3 or later.
2. Setuptools 12.2 or later.
3. Nose 1.3.4 or later for Python 3 to run any unit tests.
4. cx_Oracle 5.1.3 or later, Oracle Instant Client for Oracle connectivity.
5. lxml 3.3.3 or later for XSLT support.


## Bundling

To create a distribution package, run:

    python3 setup.py sdist


## Installation

To install the application:

1. Copy the `rattle.X.X.tar.gz` on the target machine
2. tar xf `rattle.X.X.tar.gz`
3. `cd rattle.X.X`
4. `sudo python3 setup.py install`
