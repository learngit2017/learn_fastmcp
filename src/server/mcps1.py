
from enum import StrEnum

from fastmcp import Context, FastMCP
from fastmcp.tools import tool
from fastmcp.dependencies import Depends, CurrentContext
from fastmcp.utilities.types import Image, Audio, File
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from typing import Annotated
from mcp.types import ToolAnnotations

mcp = FastMCP("My MCP server")

@mcp.tool
async def greet(name: str):
    """Greet a user by name."""
    return f"Hello, {name}!"


class Calculator:
    def __init__(self, multiplier: int = 1):
        self.multiplier = multiplier

    @tool()
    def multiply(self, x: int) -> int:
        """Multiply a number by the multiplier."""
        return x * self.multiplier  


def get_user_id() -> str:
    return "user_12345"


@mcp.tool
def get_user_details(
    user_id: str = Depends(get_user_id), 
    age: Annotated[int, Field(description="Target width in pixels", ge=6, lt=18)] = 6
    ) -> str:
    return f"User {user_id}'s age is {age}."


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


@mcp.tool
def get_image() -> Image:
    """Generate a image."""
    return Image(path="resources/image1.png")


@mcp.tool
def get_multiple_images() -> list[Image]:
    """Return multiple images."""
    return [Image(path="resources/image1.png"), Image(path="resources/image2.png")]


@mcp.tool
def get_audio() -> Audio:
    """Return an audio file."""
    return Audio(path="resources/audio1.mp3")

@mcp.tool
def get_file() -> File:
    """Return a file."""
    return File(path="resources/sample.txt")

class OrderSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class Decision(StrEnum):
    ACCEPT = "accept"
    DECLINE = "decline"
    CANCEL = "cancel"

# 定义弹窗收集的表单结构（Pydantic）
class LimitOrderExtra(BaseModel):
    limit_price: float
    expire_time: str

@mcp.tool(
    annotations=ToolAnnotations(
        title="提交交易订单",
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=False
    )
)
async def submit_order(
    symbol: str,
    side: OrderSide,
    qty: float,
    order_type: OrderType,
    ctx: Context = CurrentContext()
) -> dict:
    """
    提交OMS订单, 限价单必须传入limit_price; 缺失时自动弹窗收集
    """
    extra = None
    if order_type == OrderType.LIMIT:
        # 发起elicitation，弹出表单
        res = await ctx.elicit(
            message="限价单需要补充限价价格与有效期",
            response_type=LimitOrderExtra
        )
        # 分支判断用户行为
        if res.action == Decision.ACCEPT.value:
            extra = res.data
        elif res.action == Decision.DECLINE.value:
            return {"result": "用户拒绝填写限价参数，订单终止"}
        elif res.action == Decision.CANCEL.value:
            return {"result": "用户取消弹窗，订单终止"}

    return {
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "order_type": order_type,
        "limit_price": extra.limit_price if extra else None,
        "expire_time": extra.expire_time if extra else None,
        "status": "NEW"
    }

if __name__ == "__main__":
    calculator = Calculator(multiplier=2)
    mcp.add_tool(calculator.multiply)
    mcp.run(transport="http",  port=8111)