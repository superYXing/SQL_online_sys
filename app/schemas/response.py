from pydantic import BaseModel
from typing import Any, Optional

class BaseResponse(BaseModel):
    """基础响应模式"""
    code: int
    message: str
    data: Optional[Any] = None
    
    class Config:
        json_encoders = {
            # 可以在这里添加自定义编码器
        } 