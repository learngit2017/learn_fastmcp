
import base64
import json

from fastmcp import FastMCP

PAGE_SIZE = 3

server = FastMCP(list_page_size=PAGE_SIZE)


@server.tool
def tool_1() -> str:
    return "tool1"

@server.tool
def tool_2() -> str:
    return "tool2"

@server.tool
def tool_3() -> str:
    return "tool3"

@server.tool
def tool_4() -> str:
    return "tool4"

@server.tool
def tool_5() -> str:
    return "tool5"


mock_data = [f"data {i}" for i in range(1, 21)]


def decode_cursor(cursor: str | None = None) -> int:
    if cursor is None:
        return 0

    raw_cursor = json.loads(base64.b64decode(cursor.encode("utf-8")).decode("utf-8"))
    return raw_cursor["offset"]

def encode_cursor(offset: int) -> str:
    raw_cursor = {"offset": offset}
    return base64.b64encode(json.dumps(raw_cursor).encode("utf-8")).decode("utf-8")


@server.tool
def get_items(cursor: str | None = None) -> dict:

    offset = 0 if cursor is None else decode_cursor(cursor)
    next_offset = offset + PAGE_SIZE
    next_cursor = None if (next_offset >= len(mock_data)) else encode_cursor(next_offset)
    items = mock_data[offset:next_offset]
    
    return {
        "items": items, 
        "next_cursor": next_cursor
    }

if __name__ == "__main__":
    server.run(transport="http",  port=8113)
