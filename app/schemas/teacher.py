from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class TeacherProfileResponse(BaseModel):
    """教师个人信息响应模型"""
    teacher_id: str
    teacher_name: str
    semester_name: str


    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "teacher_id": "201992012",
                "teacher_name": "刘晓",
                "semester_name": "2025年春季",
            }
        }

class CourseInfo(BaseModel):
    """课程信息模型"""
    course_id: str
    course_name: str
    semester_name: str
    student_count: int
    
    class Config:
        from_attributes = True

class TeacherCourseListResponse(BaseModel):
    """教师课程列表响应模型"""
    courses: List[CourseInfo]
    total: int
    
    class Config:
        from_attributes = True

class StudentGradeInfo(BaseModel):
    """学生成绩信息模型"""
    student_id: str
    student_name: str
    class_name: str
    total_problems: int
    correct_problems: int
    score: float
    
    class Config:
        from_attributes = True

class CourseGradeResponse(BaseModel):
    """课程成绩响应模型"""
    course_id: str
    course_name: str
    students: List[StudentGradeInfo]
    total_students: int

    class Config:
        from_attributes = True

# 学生管理相关模型
class StudentCreateRequest(BaseModel):
    """教师创建学生请求模型"""
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

class StudentCreateResponse(BaseModel):
    """学生创建响应模型"""
    id: int
    student_id: str
    student_name: str
    class_: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "student_id": "20232251177",
                "student_name": "张三",
                "class_": "计算机科学与技术1班"
            }
        }

# 学生选课相关模型
class StudentCourseItem(BaseModel):
    """单个学生选课信息模型"""
    student_id: str
    student_name: str
    class_: str
    status: int  # 0为正常，1为重修
    course_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "20232251177",
                "student_name": "张三",
                "class_": "计算机科学与技术1班",
                "status": 0,
                "course_id": 10
            }
        }

class StudentCourseAddRequest(RootModel[List[StudentCourseItem]]):
    """添加学生选课信息请求模型（支持批量）"""
    root: List[StudentCourseItem]

    class Config:
        json_schema_extra = {
            "example": [
                {
                    "student_id": "20232251177",
                    "student_name": "张三",
                    "class_": "计算机科学与技术1班",
                    "status": 0,
                    "course_id": 10
                },
                {
                    "student_id": "20234651182",
                    "student_name": "李四",
                    "class_": "计算机科学与技术1班",
                    "status": 1,
                    "course_id": 10
                }
            ]
        }

class StudentCourseAddResponse(BaseModel):
    """添加学生选课信息响应模型"""
    code: int = 200
    msg: str = "添加成功"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "添加成功"
            }
        }

# 数据库模式相关模型
class SQLFileContent(BaseModel):
    """SQL文件内容模型"""
    mysql_engine: str
    postgresql_opengauss_engine: str

class SchemaCreateRequest(BaseModel):
    """创建数据库模式请求模型"""
    schema_description: str  # HTML格式文本描述
    schema_name: str
    sql_file_content: SQLFileContent  # SQL建表语句对象
    sql_schema: str
    schema_author: str  # 模式作者

    class Config:
        json_schema_extra = {
            "example": {
                "schema_description": "<html><body><h1>test</h1></body></html>",
                "schema_name": "test",
                "sql_file_content": {
                    "mysql_engine": "create table",
                    "postgresql_opengauss_engine": "create table"
                },
                "sql_schema": "test",
                "schema_author": "李师师"
            }
        }

class SchemaCreateResponse(BaseModel):
    """创建数据库模式响应模型"""
    code: int = 200
    msg: str = "创建数据库模式成功"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "创建数据库模式成功"
            }
        }

class SQLQueryRequest(BaseModel):
    """SQL查询请求模型"""
    schema_id: int
    sql: str

    class Config:
        json_schema_extra = {
            "example": {
                "schema_id": 4,
                "sql": "SELECT * FROM test"
            }
        }

class SQLQueryResponse(BaseModel):
    """SQL查询响应模型"""
    code: int = 200
    msg: str = "查询成功"
    columns: List[str] = []
    rows: List[List] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "查询成功",
                "columns": ["EMPLOYEE_ID", "FIRST_NAME", "LAST_NAME", "EMAIL", "PHONE_NUMBER", "HIRE_DATE", "JOB_ID", "SALARY", "COMMISSION_PCT", "MANAGER_ID", "DEPARTMENT_ID"],
                "rows": [
                    [100, "Steven", "King", "SKING", "515.123.4567", "2003-06-17 00:00:00", "AD_PRES", 24000, None, None, 90],
                    [101, "Neena", "Kochhar", "NKOCHHAR", "515.123.4568", "2005-09-21 00:00:00", "AD_VP", 17000, None, 100, 90]
                ]
            }
        }



# 分数核算相关模型
class ScoreCalculateRequest(BaseModel):
    """分数核算请求模型"""
    problem_ids: List[int]

    class Config:
        json_schema_extra = {
            "example": {
                "problem_ids": [5, 6, 7, 8]
            }
        }

class StudentScoreInfo(BaseModel):
    """学生分数信息模型"""
    course_id: int
    student_id: str
    student_name: str
    class_: str = ""
    total_score: int

    class Config:
        from_attributes = True

class ScoreUpdateResponse(BaseModel):
    """分数更新响应模型"""
    code: int = 200
    msg: str = "更新分数成功"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "更新分数成功"
            }
        }

class ScoreListResponse(BaseModel):
    """学生分数列表响应模型"""
    code: int = 200
    msg: str = ""
    scorelist: List[StudentScoreInfo]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "",
                "scorelist": [
                    {
                        "course_id": "03",
                        "student_id": "1",
                        "student_name": "王欧式",
                        "class": "软件2211班",
                        "total_score": 85
                    }
                ]
            }
        }

# 教师端题目和模式相关响应模型
class TeacherProblemItem(BaseModel):
    """教师端题目项模型"""
    problem_id: int
    is_required: int
    problem_content: str

    class Config:
        from_attributes = True

class TeacherProblemListResponse(BaseModel):
    """教师端题目列表响应模型"""
    schema_name: str
    problems: List[TeacherProblemItem]

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
                    },
                    {
                        "problem_id": 6,
                        "is_required": 0,
                        "problem_content": "查询部门平均薪资"
                    }
                ]
            }
        }

class TeacherSchemaItem(BaseModel):
    """教师端数据库模式项模型"""
    schema_id: int
    schema_name: str

    class Config:
        from_attributes = True

class TeacherSchemaListResponse(BaseModel):
    """教师端数据库模式列表响应模型"""
    schemas: List[TeacherSchemaItem]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": [
                {
                    "schema_id": 1,
                    "schema_name": "ORACLE_HR"
                },
                {
                    "schema_id": 2,
                    "schema_name": "DATABASE_HR"
                }
            ]
        }

# SQL查询相关模型已在上方定义，避免重复

# 学期相关模型
class SemesterItem(BaseModel):
    """学期项模型"""
    semester_id: int
    semester_name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    class Config:
        from_attributes = True

class SemesterListResponse(BaseModel):
    """学期列表响应模型"""
    semesters: List[SemesterItem]
    total: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "semesters": [
                    {
                        "semester_id": 1,
                        "semester_name": "2024年春季学期",
                        "start_date": "2024-02-26",
                        "end_date": "2024-07-15"
                    }
                ],
                "total": 1
            }
        }

# 已删除: 态势矩阵相关模型 - 接口已废弃
# SchemaStats, SemesterMatrix, DashboardMatrixResponse

# 学生题目提交情况相关模型
class StudentProblemStatsRequest(BaseModel):
    """学生题目提交情况查询请求模型"""
    student_ids: List[str]
    problem_ids: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "student_ids": ["20222241236", "20212261879", "202362618852"],
                "problem_ids": ["1", "2", "3"]
            }
        }

# 学生答题记录查询相关模型
class StudentAnswerRecordsRequest(BaseModel):
    """学生答题记录查询请求模型"""
    semester_ids: List[int]

    class Config:
        json_schema_extra = {
            "example": {
                "semester_ids": [1, 2]
            }
        }

class StudentAnswerRecord(BaseModel):
    """学生答题记录模型"""
    student_id: str
    problem_content: str
    result_type: int  # 0:正确  1：语法错误  2：结果错误
    answer_content: str
    timestep: str

    class Config:
        from_attributes = True

class StudentAnswerRecordsResponse(BaseModel):
    """学生答题记录响应模型"""
    data: List[StudentAnswerRecord]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "student_id": "20222241236",
                        "problem_content": "content",
                        "result_type": 0,
                        "answer_content": "select from",
                        "timestep": "2025-06-22 16:15:47"
                    },
                    {
                        "student_id": "20222241236",
                        "problem_content": "content",
                        "result_type": 0,
                        "answer_content": "select from",
                        "timestep": "2025-06-22 16:15:47"
                    }
                ]
            }
        }

class StudentProblemStat(BaseModel):
    """学生题目统计模型"""
    student_id: str
    problem_id: str
    submit_count: int
    correct_count: int
    syntax_error_count: int
    result_error_count: int

    class Config:
        from_attributes = True

class StudentProblemStatsResponse(BaseModel):
    """学生题目提交情况响应模型"""
    data: List[StudentProblemStat]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "student_id": "20222241236",
                        "problem_id": "2",
                        "submit_count": 1,
                        "correct_count": 1,
                        "syntax_error_count": 0,
                        "result_error_count": 0
                    },
                    {
                        "student_id": "20212261879",
                        "problem_id": "2",
                        "submit_count": 1,
                        "correct_count": 1,
                        "syntax_error_count": 0,
                        "result_error_count": 0
                    }
                ]
            }
        }

# 提交记录模型（保留用于其他接口）
class SubmissionRecord(BaseModel):
    """提交记录模型"""
    submission_time: str
    sql_content: str
    result_type: int  # 0:正确  1：语法错误  2：结果错误
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

# 学生答题概况相关模型
class StudentProfileResponse(BaseModel):
    """学生答题概况响应模型"""
    student_id: str
    student_name: str
    class_name: str
    total_problems: int
    completed_problems: int
    correct_problems: int
    completion_rate: float
    accuracy_rate: float
    last_submission_time: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "student_id": "20232251177",
                "student_name": "张三",
                "class_name": "计算机科学与技术1班",
                "total_problems": 10,
                "completed_problems": 8,
                "correct_problems": 6,
                "completion_rate": 80.0,
                "accuracy_rate": 75.0,
                "last_submission_time": "2024-03-15 14:30:00"
            }
        }

# 获取学生信息接口相关模型
class StudentInfoResponse(BaseModel):
    """获取学生信息响应模型"""
    code: int = 200
    msg: str = "查询成功"
    data: Dict[str, Any]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "查询成功",
                "data": {
                    "student_id": "20232251177",
                    "student_name": "张三",
                    "class": "计算机科学与技术1班"
                }
            }
        }

# 学生答题概况接口相关模型
class StudentProfileData(BaseModel):
    """学生答题概况数据模型"""
    student_id: str
    student_name: str
    class_: str = Field(..., alias="class")
    total_problems: int
    completed_problems: int
    correct_problems: int
    completion_rate: float
    accuracy_rate: float
    last_submission_time: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class StudentProfileNewResponse(BaseModel):
    """学生答题概况新响应模型"""
    code: int = 200
    msg: str = "查询成功"
    data: StudentProfileData

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "查询成功",
                "data": {
                    "student_id": "20232251177",
                    "student_name": "张三",
                    "class": "计算机科学与技术1班",
                    "total_problems": 10,
                    "completed_problems": 8,
                    "correct_problems": 6,
                    "completion_rate": 80.0,
                    "accuracy_rate": 75.0,
                    "last_submission_time": "2024-03-15 14:30:00"
                }
            }
        }

# 学生答题概况接口（按文档要求）相关模型
class StudentProfileDocResponse(BaseModel):
    """学生答题概况响应模型（按文档要求）"""
    student_id: str
    student_name: str
    class_name: str
    course_id: int
    status: int
    correct_count: int
    submit_count: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "student_id": "20232261107",
                "student_name": "刘东",
                "class_name": "2023级7班",
                "course_id": 3,
                "status": 0,
                "correct_count": 1,
                "submit_count": 4
            }
        }

# 获取学生详细信息接口相关模型
class StudentDetailResponse(BaseModel):
    """获取学生详细信息响应模型"""
    id: int
    student_id: str
    student_name: Optional[str] = None
    class_: Optional[str] = Field(None, alias="class")
    course_id: int

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "student_id": "20232251177",
                "student_name": "张三",
                "class": "计算机科学与技术1班",
                "course_id": 3
            }
        }



# 题目统计相关模型
class ProblemStatItem(BaseModel):
    """题目统计项模型"""
    problem_id: int
    problem_content: str
    total_submissions: int
    correct_submissions: int
    unique_students: int
    accuracy_rate: float

    class Config:
        from_attributes = True

class ProblemStatisticsResponse(BaseModel):
    """题目统计响应模型"""
    schema_id: int
    schema_name: str
    problems: List[ProblemStatItem]
    total_problems: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "schema_id": 1,
                "schema_name": "ORACLE_HR",
                "problems": [
                    {
                        "problem_id": 5,
                        "problem_content": "查询所有员工信息",
                        "total_submissions": 150,
                        "correct_submissions": 120,
                        "unique_students": 50,
                        "accuracy_rate": 80.0
                    }
                ],
                "total_problems": 1
            }
        }

# 学生题目统计汇总相关模型
class StudentProblemStatItem(BaseModel):
    """学生题目统计项模型"""
    student_name: str
    class_: str = Field(..., alias="class")
    problem_id: int
    correct_count: int
    submit_count: int

    class Config:
        from_attributes = True
        populate_by_name = True

class StudentProblemStatisticsResponse(BaseModel):
    """学生题目统计汇总响应模型"""
    code: int = 200
    msg: str = "查询成功"
    data: List[StudentProblemStatItem]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "查询成功",
                "data": [
                    {
                        "student_name": "张三",
                        "class": "软件2301",
                        "problem_id": 5,
                        "correct_count": 1,
                        "submit_count": 2
                    },
                    {
                        "student_name": "李四",
                        "class": "软件2302",
                        "problem_id": 5,
                        "correct_count": 0,
                        "submit_count": 3
                    }
                ]
            }
        }

# 题目完成情况统计相关模型
class ProblemSummaryItem(BaseModel):
    """题目完成情况统计项模型"""
    problem_id: int
    problem_content: str
    completed_count: int
    total_submissions: int

    class Config:
        from_attributes = True

class ProblemSummaryResponse(BaseModel):
    """题目完成情况统计响应模型"""
    problems: List[ProblemSummaryItem]
    total_problems: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "problems": [
                    {
                        "problem_id": 5,
                        "problem_content": "查询所有员工信息",
                        "completed_count": 35,
                        "total_submissions": 150
                    }
                ],
                "total_problems": 1
            }
        }



# 数据库模式修改相关模型
class SchemaUpdateRequest(BaseModel):
    """数据库模式修改请求模型"""
    schema_id: int
    schema_description: str
    schema_name: str
    sql_file_content: Optional[str] = None  # SQL建表语句文本内容（可选）
    sql_schema: str
    schema_author: Optional[str] = None  # 模式作者（可选）

    class Config:
        json_schema_extra = {
            "example": {
                "schema_id": 1,
                "schema_description": "<html><body><h1>test</h1></body></html>",
                "schema_name": "test",
                "sql_file_content": "select * from ...",
                "sql_schema": "test"
                # schema_author 为可选字段，可以不传入
            }
        }

class SchemaUpdateResponse(BaseModel):
    """数据库模式修改响应模型"""
    code: int = 200
    msg: str = "修改数据库模式成功"

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "修改数据库模式成功"
            }
        }

# 学生分数相关模型（按接口文档格式）
class StudentScoreItem(BaseModel):
    """学生分数项模型"""
    course_id: str
    student_id: str
    student_name: str
    class_: str = Field(alias="class")  # 使用alias处理class关键字
    status: str
    total_score: int

    class Config:
        from_attributes = True
        populate_by_name = True  # 允许使用字段名和别名
        json_schema_extra = {
            "example": {
                "course_id": "03",
                "student_id": "1",
                "student_name": "王欧式",
                "class": "软件2211班",
                "status": "1",
                "total_score": 85
            }
        }

class StudentScoreListResponse(BaseModel):
    """学生分数列表响应模型"""
    code: int = 200
    msg: str = ""
    scorelist: List[StudentScoreItem]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "",
                "scorelist": [
                    {
                        "course_id": "03",
                        "student_id": "1",
                        "student_name": "王欧式",
                        "class": "软件2211班",
                        "status": "1",
                        "total_score": 85
                    }
                ]
            }
        }

# 教师题目列表相关模型（按接口文档格式）
class TeacherProblemItem(BaseModel):
    """教师题目项模型"""
    problem_id: int
    is_required: int  # 是否为必做题
    is_ordered: int   # 是否有序
    problem_content: str
    example_sql: str

    class Config:
        from_attributes = True

class TeacherProblemListData(BaseModel):
    """教师题目列表数据模型"""
    problems: List[TeacherProblemItem] = []

    class Config:
        from_attributes = True

class TeacherProblemListDocResponse(BaseModel):
    """教师题目列表响应模型（按接口文档格式）"""
    code: int = 200
    msg: str = "查询成功"
    data: List[TeacherProblemItem]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "查询成功",
                "data": [
                    {
                        "problem_id": 6,
                        "is_required": 1,
                        "is_ordered": 0,
                        "problem_content": "查询员工信息",
                        "example_sql": "SELECT * FROM EMPLOYEES"
                    }
                ]
            }
        }

# 题目统计相关模型（按接口文档格式）
class ProblemSummaryData(BaseModel):
    """题目统计数据模型"""
    problem_id: int
    completed_student_count: int  # 完成此题目的学生人数
    total_submission_count: int   # 此题目的总提交次数

    class Config:
        from_attributes = True

class ProblemSummaryDocResponse(BaseModel):
    """题目统计响应模型（按接口文档格式）"""
    code: int = 200
    msg: str = "查询成功"
    data: ProblemSummaryData

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "查询成功",
                "data": {
                    "problem_id": 11,
                    "completed_student_count": 121,
                    "total_submission_count": 449
                }
            }
        }

# 题目详情和编辑相关模型
class ProblemDetailData(BaseModel):
    """题目详情数据模型"""
    problem_id: int
    is_required: int
    is_ordered: int
    problem_content: str
    example_sql: str

    class Config:
        from_attributes = True

class ProblemDetailResponse(BaseModel):
    """题目详情响应模型（按接口文档格式）"""
    code: int
    msg: str
    data: ProblemDetailData

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "查询成功",
                "data": {
                    "problem_id": 6,
                    "is_required": 1,
                    "is_ordered": 0,
                    "problem_content": "资的1.3倍\n3. 查询的结果包括以下字段：\n    1. 员工姓名（firstname+空格+lastname格式形成一个资",
                    "example_sql": "FROM EMPLOYEES e3 WHERE e3.DEPARTMENT_ID =e2.DEPARTMENT_ID "
                }
            }
        }

class ProblemEditRequest(BaseModel):
    """题目编辑请求模型（按接口文档要求）"""
    problem_id: int
    is_required: Optional[int] = None
    is_ordered: Optional[int] = None
    problem_content: Optional[str] = None
    example_sql: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "problem_id": 6,
                "is_required": 1,
                "is_ordered": 0,
                "problem_content": "资的1.3倍\n3. 查询的结果包括以下字段：\n    1. 员工姓名（firstname+空格+lastname格式形成一个资",
                "example_sql": "FROM EMPLOYEES e3 WHERE e3.DEPARTMENT_ID =e2.DEPARTMENT_ID "
            }
        }

class ProblemEditResponse(BaseModel):
    """题目编辑响应模型（按接口文档要求）"""
    code: int
    msg: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "题目更新成功"
            }
        }

# 题目创建相关模型
class ProblemCreateRequest(BaseModel):
    """题目创建请求模型"""
    is_required: int
    is_ordered: int
    problem_content: str
    example_sql: str
    schema_id: Optional[int] = None  # 可选的数据库模式ID

    class Config:
        json_schema_extra = {
            "example": {
                "is_required": 1,
                "is_ordered": 0,
                "problem_content": "资的1.3倍\n3. 查询的结果包括以下字段：\n    1. 员工姓名（firstname+空格+lastname格式形成一个资",
                "example_sql": "FROM EMPLOYEES e3 WHERE e3.DEPARTMENT_ID =e2.DEPARTMENT_ID ",
                "schema_id": 1
            }
        }

class ProblemCreateResponse(BaseModel):
    """题目创建响应模型"""
    code: int = 200
    msg: str = "题目创建成功"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "题目创建成功"
            }
        }

# 学生信息管理相关模型
class StudentDetailInfo(BaseModel):
    """学生详细信息模型（包含课程ID）"""
    id: int
    student_id: str
    student_name: Optional[str]
    class_: Optional[str]
    course_id: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "student_id": "20232251177",
                "student_name": "张三",
                "class_": "计算机科学与技术1班",
                "course_id": 10
            }
        }

class StudentUpdateRequest(BaseModel):
    """学生信息更新请求模型"""
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

class StudentUpdateResponse(BaseModel):
    """学生信息更新响应模型"""
    code: int = 200
    msg: str = "更新成功"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "更新成功"
            }
        }

class ProblemDeleteResponse(BaseModel):
    """题目删除响应模型"""
    code: int
    msg: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "题目删除成功"
            }
        }

# 教师端学生列表相关模型
class TeacherStudentInfo(BaseModel):
    """教师端学生信息模型"""
    student_id: str
    student_name: str
    class_: str
    teacher_name: str
    semester_name: str
    course_id: str

    class Config:
        from_attributes = True

class TeacherStudentListResponse(BaseModel):
    """教师端学生列表响应模型"""
    students: List[TeacherStudentInfo]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "students": [
                    {
                        "student_id": "20232251177",
                        "student_name": "张三",
                        "class_": "计算机科学与技术1班",
                        "teacher_name": "赵欧式",
                        "semester_name": "2025年春季",
                        "course_id": "1"
                    }
                ],
                "total": 1,
                "page": 1,
                "limit": 20
            }
        }
