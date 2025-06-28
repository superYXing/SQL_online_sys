from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class SemesterUpdateRequest(BaseModel):
    """学期时间更新请求模型"""
    semester_id: int
    begin_date: date
    end_date: date
    
    class Config:
        json_schema_extra = {
            "example": {
                "semester_id": 1,
                "begin_date": "2025-02-01",
                "end_date": "2025-06-30"
            }
        }

class SemesterInfo(BaseModel):
    """学期信息模型"""
    semester_id: int
    semester_name: Optional[str]
    begin_date: Optional[date]
    end_date: Optional[date]
    date_id: str
    
    class Config:
        from_attributes = True

class SemesterUpdateResponse(BaseModel):
    """学期更新响应模型"""
    success: bool
    message: str
    semester: SemesterInfo

    class Config:
        from_attributes = True

# 教师管理相关模型
class TeacherCreateRequest(BaseModel):
    """创建教师请求模型"""
    teacher_id: str
    teacher_name: str
    teacher_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "teacher_id": "T001",
                "teacher_name": "张老师",
                "teacher_password": "123456"
            }
        }

class TeacherInfo(BaseModel):
    """教师信息模型"""
    id: int
    teacher_id: str
    teacher_name: Optional[str]

    class Config:
        from_attributes = True

class TeacherUpdateRequest(BaseModel):
    """更新教师请求模型"""
    teacher_name: Optional[str] = None
    teacher_password: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "teacher_name": "张老师",
                "teacher_password": "new_password"
            }
        }

class TeacherListResponse(BaseModel):
    """教师列表响应模型"""
    teachers: List[TeacherInfo]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True

# 学生管理相关模型
class StudentCreateRequest(BaseModel):
    """创建学生请求模型"""
    student_id: str
    student_name: str
    class_: str
    student_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "20232251177",
                "student_name": "张三",
                "class_": "计算机科学与技术1班",
                "student_password": "123456"
            }
        }

class StudentInfo(BaseModel):
    """学生信息模型"""
    id: int
    student_id: str
    student_name: Optional[str]
    class_: Optional[str]

    class Config:
        from_attributes = True

class StudentUpdateRequest(BaseModel):
    """更新学生请求模型"""
    student_name: Optional[str] = None
    class_: Optional[str] = None
    student_password: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "student_name": "张三",
                "class_": "计算机科学与技术1班",
                "student_password": "new_password"
            }
        }

class StudentListResponse(BaseModel):
    """学生列表响应模型"""
    students: List[StudentInfo]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True

# 学期管理相关模型
class SemesterCreateRequest(BaseModel):
    """创建学期请求模型"""
    semester_name: str
    begin_date: date
    end_date: date

    class Config:
        json_schema_extra = {
            "example": {
                "semester_name": "2025-2026学年第一学期",
                "begin_date": "2025-09-01",
                "end_date": "2026-01-15"
            }
        }

class SemesterListResponse(BaseModel):
    """学期列表响应模型"""
    semesters: List[SemesterInfo]
    total: int

    class Config:
        from_attributes = True

# 数据库模式管理相关模型
class DatabaseSchemaCreateRequest(BaseModel):
    """创建数据库模式请求模型"""
    schema_name: str
    schema_description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "schema_name": "员工管理系统",
                "schema_description": "包含员工、部门、薪资等表的数据库模式"
            }
        }

class DatabaseSchemaUpdateRequest(BaseModel):
    """更新数据库模式请求模型"""
    schema_name: Optional[str] = None
    schema_description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "schema_name": "员工管理系统（更新）",
                "schema_description": "更新后的数据库模式描述"
            }
        }

class DatabaseSchemaInfo(BaseModel):
    """数据库模式信息模型"""
    schema_id: int
    schema_name: Optional[str]
    schema_description: Optional[str]

    class Config:
        from_attributes = True

class DatabaseSchemaListResponse(BaseModel):
    """数据库模式列表响应模型"""
    schemas: List[DatabaseSchemaInfo]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True

# 通用响应模型
class OperationResponse(BaseModel):
    """通用操作响应模型"""
    success: bool
    message: str

    class Config:
        from_attributes = True
