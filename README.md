# Magic Box Python [![Slack Status](https://fuzz-opensource.herokuapp.com/badge.svg)](https://fuzz-opensource.herokuapp.com/)

## DEVELOPMENT

### SETUP

Create your virtual environment:

    $ virtualenv -p python3 magicbox-env

If you don't have virtualenv installed:

    $ sudo pip install virtualenv

You will probably want to upgrade to the latest pip

    $ pip install --upgrade pip

Activate virtual env

    $ source bi-dw-env/bin/activate

You can deactivate this by typing `deactivate`

Install dev dependencies

	$ pip install -r requirements.txt


### TESTING

See _important_ note below about how to run the debugger with nose.

To run the test suite:

    $ ./setup.py test

Or just a file:

    $ ./setup.py test tests/test_app.py

Or just a Class in a file:

    $ ./setup.py test tests/test_app.py:TestApp

Or a test in a Class:

    $ ./setup.py test tests/test_app.py:TestApp.test_the_testing


### PEP8 Compliance

We maintain PEP8 compliance:

    * Use spaces, not tabs
    * Indent 4 spaces
    * ...

You can test your code's compliance with:

    $ pep8 some/file/or/dir


# TODO:

- Need to make valid test suite
- Write a better readme
- A lot more coding...
