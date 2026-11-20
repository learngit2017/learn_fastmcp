import asyncio
from fastmcp import Client



async def call_tool(name: str):
    async with Client("http://localhost:8111/mcp") as client:
        print(client)
        result = await client.call_tool("greet", {"name": name})
        print(result)


asyncio.run(call_tool("Alice"))
    