import sys

from app import loop

if __name__ == '__main__':
    if len(sys.argv) == 2:
        base_url = str(sys.argv[1])
        loop.kickoff(base_url)
    else:
        loop.kickoff()
