import os

from app import loop

DEFAULT_URL = 'https://ripe.knukro.com/api'

print('Test')

if __name__ == '__main__':
    base_url = os.environ.get('BASE_URL')
    if base_url is not None:
        loop.kickoff(base_url)
    else:
        loop.kickoff(DEFAULT_URL)
