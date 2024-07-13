import asyncio
from app import loop

if __name__ == "__main__":
    asyncio.run(loop.kickoff())
