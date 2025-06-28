from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

class CurrentSemesterResponse(BaseModel):
    """当前学期响应模型"""
    semester_id: int
    semester_name: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "semester_id": 1,
                "semester_name": "2024年第一学期"
            }
        }

class SemesterInfo(BaseModel):
    """学期信息模型"""
    semester_id: int
    semester_name: str
    begin_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    
    class Config:
        from_attributes = True

class SemesterListResponse(BaseModel):
    """学期列表响应模型"""
    semesters: List[SemesterInfo]
    total: int
    current_semester: Optional[CurrentSemesterResponse] = None
    
    class Config:
        from_attributes = True

class SystemInfoResponse(BaseModel):
    """系统信息响应模型"""
    system_name: str = "SQL在线平台"
    version: str = "1.0.0"
    current_time: datetime
    current_semester: Optional[CurrentSemesterResponse] = None
    
    class Config:
        from_attributes = True

class DatabaseSchemaPublicInfo(BaseModel):
    """公共数据库模式信息模型"""
    schema_id: int
    schema_name: Optional[str]
    schema_description: Optional[str]
    
    class Config:
        from_attributes = True

class DatabaseSchemaPublicListResponse(BaseModel):
    """公共数据库模式列表响应模型"""
    schemas: List[DatabaseSchemaPublicInfo]
    total: int
    
    class Config:
        from_attributes = True
