import subprocess
import time
import atexit
import requests as re
import signal

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
        print(f'[Watchdog] Ripe is up to date: {local_sha}')
        return

    # update ripe
    subprocess.run(['git', 'config', 'pull.rebase', 'false'])
    subprocess.run(['git', 'config', 'user.email' 'RIPE-watchdog@example.com'])
    subprocess.run(['git', 'config', 'user.name' 'Ripe Watchdog'])
    status = subprocess.run(['git', 'pull', 'origin', 'main'])
    if status.returncode != 0:
        raise OSError('Failed pulling master')
    status = subprocess.run(['pip3', 'install', '-r', 'requirements.txt'])
    if status.returncode != 0:
        raise OSError('Failed installing dependencies')

    updated_sha = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()

    print(f'[Watchdog] Restarting ripe with: {updated_sha}')
    if APP is not None:
        APP.kill()
    APP = run_app()


atexit.register(cleanup)
signal.signal(signal.SIGUSR1, lambda x, y: hot_reload_if_necessary)

APP = run_app()
while True:
    time.sleep(1)
    if APP.poll() is not None:
        print('[Watchdog] Ripe terminated restarting..')
        APP = run_app()

    if LAST_UPDATE is None or (datetime.now() - LAST_UPDATE) >= timedelta(hours=6):
        try:
            hot_reload_if_necessary()
            LAST_UPDATE = datetime.now()
        except Exception as e:
            print(f'[Watchdog] Failed to hot reload application {e}')
