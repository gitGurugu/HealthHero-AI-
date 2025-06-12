from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    message: str = Field(..., description="用户输入的消息内容")


class ChatResponse(BaseModel):
    code: int = Field(0, description="响应状态码，0表示成功")
    data: dict = Field(..., description="响应数据，包含AI助手的回复内容")
    msg: str = Field("success", description="响应消息，默认值为'success'")