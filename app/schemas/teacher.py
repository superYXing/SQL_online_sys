from pydantic import BaseModel, Field
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
class StudentCourseAddRequest(BaseModel):
    """添加学生选课信息请求模型"""
    student_id: str
    student_name: str
    class_: str
    status: int  # 0为重修，1为正常
    course_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "20232251177",
                "student_name": "张三",
                "class_": "计算机科学与技术1班",
                "status": 1,
                "course_id": 10
            }
        }

class StudentCourseAddResponse(BaseModel):
    """添加学生选课信息响应模型"""
    code: int = 200
    msg: str = "查询成功"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "查询成功"
            }
        }

# 数据库模式相关模型
class SchemaCreateRequest(BaseModel):
    """创建数据库模式请求模型"""
    html_content: str

    class Config:
        json_schema_extra = {
            "example": {
                "html_content": "<table><tr><th>id</th><th>name</th></tr></table>"
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

class ImportFailDetail(BaseModel):
    """导入失败详情模型"""
    row: int
    reason: str

    class Config:
        from_attributes = True

class StudentImportResponse(BaseModel):
    """学生批量导入响应模型"""
    code: int = 200
    msg: str
    success_count: int
    fail_count: int
    fail_details: List[ImportFailDetail]

    class Config:
        from_attributes = True

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

# 态势矩阵相关模型
class SchemaStats(BaseModel):
    """数据库模式统计模型"""
    student_count: int
    problem_count: int
    submission_count: int

    class Config:
        from_attributes = True

class SemesterMatrix(BaseModel):
    """学期矩阵模型"""
    semester: str
    schemas: Dict[str, SchemaStats]

    class Config:
        from_attributes = True

class DashboardMatrixResponse(BaseModel):
    """态势矩阵响应模型"""
    code: int = 200
    msg: str = "查询成功"
    matrix: List[SemesterMatrix]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "查询成功",
                "matrix": [
                    {
                        "semester": "2025春季",
                        "schemas": {
                            "test": {
                                "student_count": 50,
                                "problem_count": 120,
                                "submission_count": 300
                            },
                            "ORACLE_HR": {
                                "student_count": 45,
                                "problem_count": 110,
                                "submission_count": 280
                            }
                        }
                    }
                ]
            }
        }

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

class StudentProblemStat(BaseModel):
    """学生题目统计模型"""
    student_id: str
    problem_id: str
    submit_count: int
    correct_count: int

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
                        "correct_count": 1
                    },
                    {
                        "student_id": "20212261879",
                        "problem_id": "2",
                        "submit_count": 1,
                        "correct_count": 1
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
    correct_count: int
    submit_count: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "student_id": "20252261107",
                "student_name": "刘东",
                "class_name": "2024级7班",
                "course_id": 3,
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

# 导出指定学生成绩数据接口相关模型
class StudentScoreExportItem(BaseModel):
    """学生成绩导出项模型"""
    student_id: str
    student_name: str
    class_: str = Field(..., alias="class")
    course_id: int
    score: int

    class Config:
        from_attributes = True
        populate_by_name = True

class StudentScoreExportRequest(BaseModel):
    """学生成绩导出请求模型"""
    students: List[StudentScoreExportItem]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "students": [
                    {
                        "student_id": "20232241177",
                        "student_name": "张三",
                        "class": "软件2301",
                        "course_id": 1,
                        "score": 20
                    },
                    {
                        "student_id": "20232241178",
                        "student_name": "李四",
                        "class": "软件2302",
                        "course_id": 2,
                        "score": 60
                    }
                ]
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

# 数据导出相关模型
class DatasetExportResponse(BaseModel):
    """数据导出响应模型"""
    schema_id: int
    schema_name: str
    export_data: Dict
    filename: str
    export_time: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "schema_id": 1,
                "schema_name": "ORACLE_HR",
                "export_data": {
                    "tables": ["employees", "departments"],
                    "problems": 10,
                    "students": 50
                },
                "filename": "ORACLE_HR_export_20240315.json",
                "export_time": "2024-03-15 14:30:00"
            }
        }

# 题目详情和编辑相关模型
class ProblemDetailData(BaseModel):
    """题目详情数据模型"""
    problem_id: int
    title: str
    problem_content: str
    example_sql: Optional[str] = None
    is_required: int

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
                    "title": "NO.6",
                    "problem_content": "找到满足如下条件的员工：\n1. 具有超过4个直接下属并且工资高于7000的直接下属员工\n2. 员工的工资高于所在部门平均工资的1.3倍",
                    "example_sql": "WITH a AS (\n  SELECT MANAGER_ID, count(*) cnt\n  FROM EMPLOYEES\n  WHERE SALARY >7000\n  GROUP BY MANAGER_ID\n)",
                    "is_required": 1
                }
            }
        }

class ProblemEditRequest(BaseModel):
    """题目编辑请求模型（按接口文档要求）"""
    problem_id: int
    problem_content: Optional[str] = None
    is_required: Optional[int] = None
    example_sql: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "problem_id": 6,
                "problem_content": "找到满足如下条件的员工：\n1. 具有超过4个直接下属且工资高于7000的直接下属员工\n2. 员工工资高于所在部门平均工资的1.3倍",
                "example_sql": "WITH managers AS (\n  SELECT MANAGER_ID, COUNT(*) AS direct_reports\n  FROM EMPLOYEES\n  WHERE SALARY > 7000\n  GROUP BY MANAGER_ID\n)",
                "is_required": 1
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

# 导出分数相关模型
class ExportStudentInfo(BaseModel):
    """导出学生信息模型"""
    student_id: str
    student_name: str
    class_: str = Field(..., alias="class")
    course_id: str
    total_score: int
    status: str

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "student_id": "20232241177",
                "student_name": "张三",
                "class": "软件2301",
                "course_id": "03",
                "total_score": 85,
                "status": "正常"
            }
        }

class ScoreExportRequest(BaseModel):
    """分数导出请求模型"""
    students: List[ExportStudentInfo]

    class Config:
        json_schema_extra = {
            "example": {
                "students": [
                    {
                        "student_id": "20232241177",
                        "student_name": "张三",
                        "class": "软件2301",
                        "course_id": "03",
                        "total_score": 85,
                        "status": "正常"
                    },
                    {
                        "student_id": "20232241178",
                        "student_name": "李四",
                        "class": "软件2302",
                        "course_id": "03",
                        "total_score": 100,
                        "status": "正常"
                    }
                ]
            }
        }
