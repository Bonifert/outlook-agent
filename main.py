from dotenv import load_dotenv
load_dotenv()
import asyncio
import json
from graph import app
from nodes.common import client


async def main():
    try:
        await client.reset_mock_db()

        result = await app.ainvoke({})
        print(json.dumps(result, indent=4, ensure_ascii=False))

    finally:
        await client.close()


asyncio.run(main())