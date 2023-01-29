import subprocess
import time
import atexit
import requests as re

from typing import Optional
from datetime import datetime, timedelta

APP: Optional[subprocess.Popen] = None
LAST_UPDATE: Optional[datetime] = None


def run_app():
    return subprocess.Popen(['python3', '-u', './ripe.py'])


def cleanup():
    global APP
    if APP is not None:
        APP.kill()


def hot_reload_if_necessary():
    global APP
    local_sha = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    remote_sha = re.get('https://api.github.com/repos/knusperkrone/RIPE-agents/commits/main', headers={
        'accept': 'application/vnd.github.VERSION.sha'
    }).text

    if local_sha == remote_sha:
        print(f'Ripe is up to date: {local_sha}')
        return

    # update ripe
    subprocess.run('git', 'pull')
    subprocess.run('pip3', '-r', 'requirements.txt')

    if APP is not None:
        APP.kill()
    APP = run_app()


atexit.register(cleanup)


APP = run_app()
while True:
    time.sleep(1)
    if APP.poll() is not None:
        print('Ripe terminated restarting..')
        APP = run_app()

    if LAST_UPDATE is None or (datetime.now() - LAST_UPDATE) >= timedelta(hours=6):
        try:
            hot_reload_if_necessary()
            LAST_UPDATE = datetime.now()
        except Exception as e:
            print(f'Failed to hot reload application {e}')
