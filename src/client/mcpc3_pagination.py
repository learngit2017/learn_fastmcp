import asyncio
from fastmcp import Client


url = "http://localhost:8113/mcp"

async def main():
    async with Client(url) as client:
      all_tools = await client.list_tools()
      print(f"All tools: {len(all_tools)}")
      for tool in all_tools:
        print(f" - {tool}")

      print("*" * 20 + "\n")

    async with Client(url) as client:
      page = await client.list_tools_mcp()
      page_num = 1
      while page:
        print(f"第{page_num}页，工具数量: {len(page.tools)}")
        if page.next_cursor is None:
          break
        page = await client.list_tools_mcp(cursor=page.next_cursor)
        page_num += 1

      print("*" * 20 + "\n")

    async with Client(url) as client:
      slice = (await client.call_tool("get_items")).data
      if slice:
        for item in slice["items"]:
          print(item)

      while (next_cursor := slice["next_cursor"]) is not None:
        slice = (await client.call_tool("get_items", {"cursor": next_cursor})).data
        for item in slice["items"]:
          print(item)
          

if __name__ == "__main__":
    asyncio.run(main())       