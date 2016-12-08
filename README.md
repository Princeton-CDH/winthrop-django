# winthrop-django

Django web application for
[The Winthrop Family on the Page](https://digitalhumanities.princeton.edu/projects/TheWinthropFamilyonthePage/)
project.

Python 3.5 / Django 1.10


## Development instructions

Initial setup and installation:

- recommended: create and activate a python 3.5 virtualenv
    `virtualenv winthrop -p python3.5`
    `source winthrop/bin/activate`

- pip install required python dependencies
    `pip install -r requirements.txt`
    `pip install -r dev-requirements.txt`

- copy sample local settings and configure for your environment
    `cp winthrop/local_settings.py.sample winthrop/local_settings.py`

(documentation TODO)
- install & configure git commit hook for Asana integration
