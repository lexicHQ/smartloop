import os

endpoint= os.getenv('BASE_URL', 'https://api.smartloop.ai/v1')
homedir = os.getenv('SLP_HOME', os.path.expanduser('~/.slp'))
