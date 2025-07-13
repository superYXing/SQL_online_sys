from pydantic import BaseModel, RootModel
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

class ProblemPublicInfo(BaseModel):
    """公共题目信息模型"""
    problem_id: int
    is_required: int
    problem_content: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "problem_id": 5,
                "is_required": 1,
                "problem_content": "查询所有员工信息"
            }
        }

class SchemaProblemsGroup(BaseModel):
    """数据库模式题目分组模型"""
    schema_name: str
    problems: List[ProblemPublicInfo]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "schema_name": "ORACLE_HR",
                "problems": [
                    {
                        "problem_id": 5,
                        "is_required": 1,
                        "problem_content": "查询所有员工信息"
                    }
                ]
            }
        }

# 公共题目列表响应类型（数组格式）
ProblemPublicListResponse = List[SchemaProblemsGroup]

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

class DatabaseSchemaListItem(BaseModel):
    """数据库模式列表项模型（新格式）"""
    schema_id: int
    schema_name: str
    schema_description: str
    schema_author: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "schema_id": 1,
                "schema_name": "ORACLE_HR",
                "schema_description": "html_description",
                "schema_author": "name"
            }
        }

class DatabaseSchemaListResponse(RootModel):
    """数据库模式列表响应模型（新格式）"""
    root: List[DatabaseSchemaListItem]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": [
                {
                    "schema_name": "ORACLE_HR",
                    "schema_description": "html_description",
                    "schema_author": "name"
                },
                {
                    "schema_name": "ORACLE_SH",
                    "schema_description": "html_description",
                    "schema_author": "name"
                }
            ]
        }

class DatabaseSchemaWithStatusItem(BaseModel):
    """包含状态的数据库模式项模型"""
    schema_id: int
    schema_name: str
    schema_description: str
    schema_author: str
    schema_status: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "schema_id": 1,
                "schema_name": "ORACLE_HR",
                "schema_description": "html_description",
                "schema_author": "name",
                "schema_status": 1
            }
        }

class DatabaseSchemaWithStatusListResponse(RootModel):
    """包含状态的数据库模式列表响应模型"""
    root: List[DatabaseSchemaWithStatusItem]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": [
                {
                    "schema_id": 1,
                    "schema_name": "ORACLE_HR",
                    "schema_description": "html_description",
                    "schema_author": "name",
                    "schema_status": 0
                },
                {
                    "schema_id": 2,
                    "schema_name": "ORACLE_SH",
                    "schema_description": "html_description",
                    "schema_author": "name",
                    "schema_status": 1
                }
            ]
        }
