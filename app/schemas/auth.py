from pydantic import BaseModel
from typing import Literal

class LoginRequest(BaseModel):
    """登录请求模式"""
    account: str
    password: str
    role: Literal["admin", "teacher", "student"]
    
    class Config:
        json_schema_extra = {
            "example": {
                "account": "20252261107",
                "password": "_s7yrhXq",
                "role": "student"
            }
        }

class UserInfo(BaseModel):
    """用户信息模式"""
    id: str
    username: str
    role: str
    
    class Config:
        from_attributes = True

class LoginData(BaseModel):
    """登录响应数据"""
    token: str
    user: UserInfo

class LoginResponse(BaseModel):
    """登录响应模式"""
    code: int = 200
    message: str = "登录成功"
    data: LoginData

class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str




