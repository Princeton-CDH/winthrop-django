# This file is exec'd from settings.py, so it has access to and can
# modify all the variables in settings.py.

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test',
        'USER': 'root',
        'HOST': 'localhost',
        'PORT': '',
        'TEST': {
                'CHARSET': 'utf8',
                'COLLATION': 'utf8_general_ci',
            },
    },
}

# required for integration tests that query Solr
SOLR_CONNECTIONS = {
  'test': {
        'COLLECTION': 'test-winthrop',
        'URL': 'http://localhost:8983/solr/',
        'ADMIN_URL': 'http://localhost:8983/solr/admin/cores'
    },
}


# secret key added as a travis build step

